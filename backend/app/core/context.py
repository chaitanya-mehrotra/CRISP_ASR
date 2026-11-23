"""Student-facing evidence from local syntax and simple assignments."""

import ast
import re

from .symbols import Symbols

SECURITY_WORDS = {"token", "password", "secret", "nonce", "otp", "session", "credential", "csrf"}


def sensitive_name(name: str) -> bool:
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().split("_")
    words = {word.rstrip("s") for word in words}
    return bool(words & SECURITY_WORDS or {"api", "key"} <= words or {"private", "key"} <= words)


def randomness_context(call: ast.Call, symbols: Symbols) -> str:
    node: ast.AST = call
    while (parent := symbols.parents.get(node)) is not None:
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return f"Function name: {parent.name}" if sensitive_name(parent.name) else ""
        if isinstance(parent, (ast.Assign, ast.AnnAssign)) and parent.value is node:
            targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
            for target in targets:
                name = target.id if isinstance(target, ast.Name) else target.attr if isinstance(target, ast.Attribute) else ""
                if sensitive_name(name):
                    return f"Assignment target: {name}"
        if isinstance(parent, ast.keyword) and parent.arg and sensitive_name(parent.arg):
            return f"Keyword argument: {parent.arg}"
        if isinstance(parent, ast.Call) and node in parent.args:
            name = parent.func.id if isinstance(parent.func, ast.Name) else parent.func.attr if isinstance(parent.func, ast.Attribute) else ""
            if sensitive_name(name):
                return f"Passed to a call named {name}"
        node = parent
    return ""


def input_origin(value: ast.expr | None, symbols: Symbols) -> str:
    """Report visible origin hints. Unknown inputs remain unknown."""
    if value is None:
        return "No direct argument was resolved."
    if isinstance(value, ast.Constant):
        return "Literal value written in this file."
    pending: list[ast.AST] = [value]
    seen: set[ast.AST] = set()
    while pending and len(seen) < 32:
        node = pending.pop()
        if node in seen:
            continue
        seen.add(node)
        scope = symbols.nodes.get(node)
        if scope is None:
            continue
        if isinstance(node, ast.Call):
            path = symbols.path(node)
            if path in {"builtins.input", "os.getenv"}:
                return f"Local input source: {path}() on line {node.lineno}."
        if isinstance(node, ast.Attribute):
            path = scope.resolve(node, node.lineno)
            if path in {"sys.argv", "os.environ"}:
                return f"Local input source: {path} on line {node.lineno}."
        if isinstance(node, ast.Name):
            owner = scope.binding_scope(node.id)
            if owner is not None:
                assignment = owner.assignments.get(node.id)
                if assignment and assignment[1] < node.lineno:
                    pending.append(assignment[0])
                args = getattr(owner.owner, "args", None)
                if isinstance(args, ast.arguments) and any(
                    isinstance(arg, ast.arg) and arg.arg == node.id for arg in ast.iter_child_nodes(args)
                ):
                    return f"Function parameter: {node.id}. Its value depends on callers."
        else:
            pending.extend(ast.iter_child_nodes(node))
    return "The argument’s origin is unresolved by local analysis. Review its callers and trust boundary."


IMPACT = {
    "CWE-95": ("If untrusted text reaches this call, the program may interpret it as code or load modules chosen by someone else.", "Does this feature need executable code, or does it only need to read data?"),
    "CWE-78": ("If external input reaches a shell command, the shell may interpret some of that input as instructions.", "Which part selects the executable, and which parts should be passed as data?"),
    "CWE-502": ("If data comes from an untrusted source, an object loader may construct unexpected objects and invoke code.", "Who controls the bytes or text being loaded?"),
    "CWE-330": ("If this value grants access, predictable randomness can make it easier for someone else to guess.", "Would predicting this value give someone access or affect a security decision?"),
    "CWE-295": ("Without certificate verification, the client may accept the wrong server as trusted.", "What would you configure if the server uses a private certificate authority?"),
    "CWE-327": ("If the digest must distinguish files securely, a weak algorithm makes it easier for different inputs to share the same digest.", "Is this value used for a security decision or only as a non-security identifier?"),
    "CWE-367": ("The file name can be taken between name generation and file creation.", "Does the function reserve the file, or does it only suggest a name?"),
    "CWE-732": ("If this file carries trusted data, another local user may be able to modify it.", "Who needs write access to this resource?"),
}


def ast_chain(call: ast.Call) -> list[str]:
    chain = ["Call"]
    node = call.func
    while isinstance(node, ast.Attribute):
        chain.append("Attribute")
        node = node.value
    chain.append(type(node).__name__)
    return chain
