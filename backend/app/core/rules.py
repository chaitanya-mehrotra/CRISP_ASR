"""Conservative AST checks. Findings identify patterns for manual review."""

import ast
from collections.abc import Callable
from dataclasses import asdict, dataclass

from .context import IMPACT, ast_chain, input_origin, randomness_context
from .repair_templates import SourceEdit, shell_edit, weak_randomness_edit, yaml_edit
from .symbols import Symbols


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    severity: str
    risk: str
    fix: str
    example: str


RULES = {
    rule.id: rule for rule in (
        Rule(
            "CWE-95", "Dynamic code evaluation", "high",
            "This call can compile text, interpret it as code, or load a module from a dynamic name. Review where the input comes from.",
            "Use json.loads for JSON data. If callers need to choose an operation, map approved names to functions. Literal-only Python input can use ast.literal_eval with an input size limit.",
            'import json\n\nsettings = json.loads(raw_json)\nif not isinstance(settings, dict):\n    raise ValueError("Expected a JSON object")',
        ),
        Rule(
            "CWE-78", "Shell command injection risk", "high",
            "Shell parsing gives special meaning to characters in command text. Review where the command and its arguments originate.",
            "Call a fixed executable with a list of separate arguments and shell=False. Validate arguments for the chosen executable and keep command names on an allowlist where users can choose them.",
            'import subprocess\nimport sys\n\nsubprocess.run(\n    [sys.executable, "-m", "my_tool", "--", validated_path],\n    shell=False, check=True,\n)',
        ),
        Rule(
            "CWE-502", "Unsafe deserialization", "high",
            "Pickle and other object-loading APIs can invoke code when loading data. Review the data’s source and trust boundary.",
            "For untrusted input, agree on a data-only format with the producer and validate the decoded data against a schema. Existing pickle files need a separate migration plan.",
            'import json\n\nrecord = json.loads(raw_json)\nif not isinstance(record, dict) or not isinstance(record.get("name"), str):\n    raise ValueError("Expected a record with a name")',
        ),
        Rule(
            "CWE-330", "Weak randomness", "medium",
            "A random-module call is used in a scope or assignment whose name suggests a token, password, secret, nonce, session, or OTP.",
            "Use secrets for security-sensitive values. Choose a token length and format that fit the application. Keep seeded random generators for simulations and reproducible tests.",
            'import secrets\n\nsession_token = secrets.token_urlsafe(32)',
        ),
        Rule(
            "CWE-295", "TLS certificate verification disabled", "high",
            "This call explicitly turns off certificate checks or creates an unverified TLS context.",
            "Keep certificate verification enabled. For private services, configure a trusted certificate authority rather than bypassing verification.",
            'import ssl\n\ncontext = ssl.create_default_context()',
        ),
        Rule(
            "CWE-327", "Weak hash algorithm", "medium",
            "MD5 and SHA-1 are unsuitable where collision resistance matters. Review whether this hash serves a security purpose.",
            "Use SHA-256 or a stronger hash where collision resistance is needed. For password storage use a dedicated password hashing library. Changing algorithms can require migrating stored digests.",
            'import hashlib\n\ndigest = hashlib.sha256(data).hexdigest()',
        ),
        Rule(
            "CWE-367", "Insecure temporary file name", "medium",
            "tempfile.mktemp returns a name without creating the file. Another process can use that name before the program opens it.",
            "Create the temporary file atomically with TemporaryFile, NamedTemporaryFile, or mkstemp. Review when it should be closed and deleted.",
            'from tempfile import TemporaryFile\n\nwith TemporaryFile() as handle:\n    handle.write(data)',
        ),
        Rule(
            "CWE-732", "World-writable file permissions", "medium",
            "This permission mode lets other local users write to the file or directory on POSIX systems.",
            "Grant write access only to users who need it. Choose the mode for the file or directory and check the deployment platform.",
            'import os\n\nos.chmod(private_file, 0o600)',
        ),
    )
}

SUBPROCESS_CALLS = {f"subprocess.{name}" for name in ("run", "Popen", "call", "check_call", "check_output")}
SHELL_CALLS = {"os.system", "os.popen"}
DYNAMIC_CALLS = {"builtins.eval", "builtins.exec", "builtins.compile", "builtins.__import__", "importlib.import_module"}
RANDOM_CALLS = {"choice", "choices", "randint", "randrange", "random", "getrandbits", "randbytes", "sample", "shuffle"}
SERIALIZERS = {
    f"{module}.{method}" for module in ("pickle", "_pickle", "cPickle", "dill", "marshal")
    for method in ("load", "loads")
} | {"joblib.load", "yaml.unsafe_load", "yaml.full_load"}


def keyword_arg(call: ast.Call, name: str) -> ast.expr | None:
    return next((entry.value for entry in call.keywords if entry.arg == name), None)


def first_arg(call: ast.Call, name: str) -> ast.expr | None:
    return call.args[0] if call.args else keyword_arg(call, name)


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "request"}
TLS_CLIENT_CALLS = {
    f"{module}.{method}" for module in ("requests", "requests.api", "httpx") for method in HTTP_METHODS
} | {"httpx.Client", "httpx.AsyncClient"}


def literal_value(node: ast.expr | None) -> object:
    return node.value if isinstance(node, ast.Constant) else None


def match_additional_rule(call: ast.Call, path: str) -> tuple[str, str] | None:
    if path == "ssl._create_unverified_context":
        return "CWE-295", "The selected factory explicitly creates an unverified TLS context."
    if path in TLS_CLIENT_CALLS and literal_value(keyword_arg(call, "verify")) is False:
        return "CWE-295", "The call sets the verify argument to False."
    algorithm = {
        "hashlib.md5": "md5",
        "hashlib.sha1": "sha1",
    }.get(path)
    if path == "hashlib.new":
        name = literal_value(first_arg(call, "name"))
        algorithm = name.lower() if isinstance(name, str) else None
    if algorithm in {"md5", "sha1"} and literal_value(keyword_arg(call, "usedforsecurity")) is not False:
        return "CWE-327", f"The call explicitly selects {algorithm.upper()}."
    if path == "tempfile.mktemp":
        return "CWE-367", "The call selects tempfile.mktemp, which returns a path without reserving the file."
    if path in {"os.chmod", "os.fchmod"}:
        mode = literal_value(call.args[1] if len(call.args) > 1 else keyword_arg(call, "mode"))
        if type(mode) is int and 0 <= mode <= 0o7777 and mode & 0o002:
            return "CWE-732", f"The literal mode {oct(mode)} includes write access for other users."
    return None


def matched_rule(call: ast.Call, path: str, symbols: Symbols) -> tuple[str, str] | None:
    if path in DYNAMIC_CALLS:
        name = "name" if path.endswith(("import_module", "__import__")) else "source"
        value = first_arg(call, name)
        if value is not None and not isinstance(value, ast.Constant):
            return "CWE-95", input_origin(value, symbols)
    if path in SHELL_CALLS | SUBPROCESS_CALLS:
        shell = keyword_arg(call, "shell")
        command = first_arg(call, "command" if path in SHELL_CALLS else "args")
        if command is not None and (path in SHELL_CALLS or isinstance(shell, ast.Constant) and shell.value is True):
            return "CWE-78", input_origin(command, symbols)
    if path == "yaml.load":
        loader = call.args[1] if len(call.args) > 1 else keyword_arg(call, "Loader")
        loader_path = symbols.nodes[call].resolve(loader, call.lineno) if loader is not None else ""
        if loader_path in {"yaml.SafeLoader", "yaml.CSafeLoader", "yaml.loader.SafeLoader", "yaml.cyaml.CSafeLoader"}:
            return None
    if path in SERIALIZERS or path == "yaml.load":
        argument = first_arg(call, "stream") or keyword_arg(call, "data") or keyword_arg(call, "file")
        return "CWE-502", input_origin(argument, symbols)
    if path.startswith("random.") and path.split(".")[-1] in RANDOM_CALLS:
        origin = randomness_context(call, symbols)
        if origin:
            return "CWE-330", origin
    return match_additional_rule(call, path)


def choose_edit(call: ast.Call, path: str, rule_id: str, lines: list[str]) -> SourceEdit | None:
    if rule_id == "CWE-330":
        return weak_randomness_edit(call, lines)
    if path == "yaml.load":
        return yaml_edit(call, lines)
    if path == "subprocess.run":
        return shell_edit(call, keyword_arg(call, "shell"), lines)
    return None


def editor_columns(lines: list[str]) -> Callable[[int, int], int]:
    """Translate UTF-8 byte offsets from Python to Monaco’s UTF-16 positions."""
    maps: dict[int, dict[int, int]] = {}

    def column(line_number: int, offset: int) -> int:
        line = lines[line_number - 1]
        if line.isascii():
            return offset + 1
        if line_number not in maps:
            byte_index, utf16_index = 0, 1
            positions = {0: 1}
            for char in line:
                byte_index += len(char.encode("utf-8"))
                utf16_index += 2 if ord(char) > 0xFFFF else 1
                positions[byte_index] = utf16_index
            maps[line_number] = positions
        return maps[line_number][offset]

    return column


def find_weaknesses(tree: ast.Module, source: str, *, include_edits: bool = False) -> list[dict]:
    symbols = Symbols(tree)
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    column = editor_columns(lines)
    has_star = any(scope.bindings["*"] for scope in symbols.scopes.values())
    modified_modules = {
        symbols.nodes[node].resolve(node.value, node.lineno)
        for node in symbols.nodes
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    findings = []
    for node in symbols.nodes:
        if not isinstance(node, ast.Call):
            continue
        path = symbols.path(node)
        match = matched_rule(node, path, symbols)
        if match is None:
            continue
        rule_id, origin = match
        edit = None if has_star or path.split(".")[0] in modified_modules else choose_edit(node, path, rule_id, lines)
        impact, question = IMPACT[rule_id]
        risk = RULES[rule_id].risk
        if path == "builtins.compile":
            risk = "This call turns a variable string into a code object. Execution risk depends on what later consumes that object."
        elif rule_id == "CWE-78" and isinstance(first_arg(node, "command" if path in SHELL_CALLS else "args"), ast.Constant):
            risk = "This command is written as a literal and still relies on shell interpretation. Review whether the shell is necessary."
        finding = {
            **asdict(RULES[rule_id]),
            "risk": risk,
            "call": path,
            "line": node.lineno,
            "column": column(node.lineno, node.col_offset),
            "end_line": node.end_lineno,
            "end_column": column(node.end_lineno, node.end_col_offset),
            "repairable": edit is not None,
            "repair_mode": ("guided" if edit.guided else "preview") if edit else "manual",
            "ast_chain": ast_chain(node),
            "origin": origin,
            "impact": impact,
            "question": question,
        }
        if include_edits:
            finding["_edit"] = edit
        findings.append(finding)
    return sorted(findings, key=lambda item: (item["line"], item["column"]))
