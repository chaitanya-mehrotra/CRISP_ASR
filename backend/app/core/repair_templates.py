"""AST-based repair templates and their exact source edits."""

import ast
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceEdit:
    line: int
    start: int
    end: int
    replacement: str
    explanation: str
    guided: bool = False

    def apply(self, line: str) -> str:
        # CPython AST columns are UTF-8 byte offsets.
        original = line.encode("utf-8")
        return (original[:self.start] + self.replacement.encode("utf-8") + original[self.end:]).decode("utf-8")


class SystemRandomTemplate(ast.NodeTransformer):
    def visit_Attribute(self, target: ast.Attribute) -> ast.Attribute:
        generator = ast.Call(
            func=ast.Attribute(value=target.value, attr="SystemRandom", ctx=ast.Load()),
            args=[],
            keywords=[],
        )
        return ast.copy_location(ast.Attribute(value=generator, attr=target.attr, ctx=ast.Load()), target)


def weak_randomness_edit(call: ast.Call, lines: list[str]) -> SourceEdit | None:
    target = call.func
    if not isinstance(target, ast.Attribute) or not isinstance(target.value, ast.Name):
        return None
    if target.lineno != target.end_lineno:
        return None

    line = lines[target.lineno - 1].encode("utf-8")
    original = line[target.col_offset:target.end_col_offset].decode("utf-8")
    if original != f"{target.value.id}.{target.attr}":
        # Avoid overwriting comments, line continuations, or unusual spacing.
        return None

    replacement = ast.unparse(SystemRandomTemplate().visit(target))
    return SourceEdit(
        target.lineno, target.col_offset, target.end_col_offset, replacement,
        "Use the operating system’s randomness while keeping the same method and arguments.",
    )


def yaml_edit(call: ast.Call, lines: list[str]) -> SourceEdit | None:
    target = call.func
    if not isinstance(target, ast.Attribute) or not isinstance(target.value, ast.Name):
        return None
    if target.lineno != target.end_lineno or len(call.args) != 1 or call.keywords:
        return None
    if isinstance(call.args[0], ast.Starred):
        return None

    line = lines[target.lineno - 1].encode("utf-8")
    if line[target.col_offset:target.end_col_offset] != f"{target.value.id}.load".encode():
        return None

    replacement = ast.unparse(ast.Attribute(value=target.value, attr="safe_load", ctx=ast.Load()))
    return SourceEdit(
        target.lineno, target.col_offset, target.end_col_offset, replacement,
        "Use the safe YAML loader. Check that your input only needs standard YAML types.",
        guided=True,
    )


FIXED_POSIX_COMMAND = re.compile(r"/(?:usr/bin|bin)/[A-Za-z0-9_.-]+(?: +[A-Za-z0-9_./-]+)*")


def shell_edit(call: ast.Call, shell: ast.expr | None, lines: list[str]) -> SourceEdit | None:
    # The narrow preview only covers an explicit POSIX executable and plain literal arguments.
    allowed = {"shell", "check", "capture_output", "text", "timeout", "encoding", "errors"}
    if len(call.args) != 1 or any(kw.arg not in allowed for kw in call.keywords):
        return None
    command = call.args[0]
    if not isinstance(command, ast.Constant) or not isinstance(command.value, str):
        return None
    if not FIXED_POSIX_COMMAND.fullmatch(command.value) or not isinstance(shell, ast.Constant):
        return None
    if not (command.lineno == command.end_lineno == shell.lineno == shell.end_lineno):
        return None

    line = lines[command.lineno - 1].encode("utf-8")
    original = line[command.col_offset:command.end_col_offset].decode()
    # Leave unusual spelling, concatenated literals, and embedded comments for review.
    if original not in (f"'{command.value}'", f'"{command.value}"'):
        return None
    arguments = ast.List(elts=[ast.Constant(arg) for arg in command.value.split()], ctx=ast.Load())
    between = line[command.end_col_offset:shell.col_offset].decode()
    return SourceEdit(
        command.lineno, command.col_offset, shell.end_col_offset,
        ast.unparse(arguments) + between + ast.unparse(ast.Constant(False)),
        "POSIX-only preview. Confirm the executable and its arguments on the deployment system.",
        guided=True,
    )
