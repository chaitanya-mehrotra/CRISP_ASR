"""Conservative lexical name resolution for static inspection."""

import ast
from collections import Counter
from dataclasses import dataclass, field

SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
               ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
BUILTINS = {"eval", "exec", "compile", "__import__", "input"}


def bound_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
        return [node.id]
    if isinstance(node, ast.arg):
        return [node.arg]
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and node.name:
        return [node.name]
    if isinstance(node, ast.MatchMapping) and node.rest:
        return [node.rest]
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return [alias.asname or alias.name.split(".")[0] for alias in node.names]
    return []


@dataclass
class Scope:
    parent: "Scope | None"
    owner: ast.AST
    bindings: Counter[str] = field(default_factory=Counter)
    imports: dict[str, tuple[str, int]] = field(default_factory=dict)
    assignments: dict[str, tuple[ast.expr, int]] = field(default_factory=dict)

    def binding_scope(self, name: str) -> "Scope | None":
        scope = self
        while scope is not None:
            if scope.bindings[name] or scope.bindings["*"]:
                return scope
            scope = scope.parent
        return None

    def resolve(self, expression: ast.AST, line: int) -> str:
        if isinstance(expression, ast.Name):
            scope = self.binding_scope(expression.id)
            if scope is None:
                return f"builtins.{expression.id}" if expression.id in BUILTINS else ""
            binding = scope.imports.get(expression.id)
            return binding[0] if binding and binding[1] < line else ""
        if isinstance(expression, ast.Attribute):
            base = self.resolve(expression.value, line)
            return f"{base}.{expression.attr}" if base else ""
        return ""


class Symbols:
    def __init__(self, tree: ast.Module):
        self.scopes: dict[ast.AST, Scope] = {}
        self.nodes: dict[ast.AST, Scope] = {}
        self.parents: dict[ast.AST, ast.AST] = {}
        self.declared = {name for node in ast.walk(tree)
                         if isinstance(node, (ast.Global, ast.Nonlocal)) for name in node.names}
        root = Scope(None, tree)
        self.scopes[tree] = root
        self._index(tree, root)
        # A declared global/nonlocal can be reassigned by a different scope.
        for scope in self.scopes.values():
            scope.bindings.update(self.declared)
            self._direct_bindings(scope)

    def _index(self, tree: ast.Module, root: Scope) -> None:
        stack = [(tree, root)]
        while stack:
            node, scope = stack.pop()
            self.nodes[node] = scope
            scope.bindings.update(bound_names(node))
            if isinstance(node, SCOPE_NODES):
                parent = scope.parent if isinstance(scope.owner, ast.ClassDef) else scope
                local = Scope(parent, node)
                self.scopes[node] = local
                for field_name, child in ast.iter_fields(node):
                    if field_name == "args" and isinstance(child, ast.arguments):
                        self._index_arguments(stack, child, scope, local)
                        continue
                    items = child if isinstance(child, list) else [child]
                    inner = field_name in {"body", "args", "elt", "key", "value", "generators"}
                    for item in items:
                        if isinstance(item, ast.AST):
                            self.parents[item] = node
                            stack.append((item, local if inner else scope))
                continue
            if isinstance(node, ast.arg):
                continue
            for child in ast.iter_child_nodes(node):
                self.parents[child] = node
                stack.append((child, scope))

    def _index_arguments(self, stack: list[tuple[ast.AST, Scope]], args: ast.arguments, scope: Scope, local: Scope) -> None:
        for child in ast.iter_child_nodes(args):
            if isinstance(child, ast.arg):
                local.bindings[child.arg] += 1
                if child.annotation is not None:
                    stack.append((child.annotation, scope))
            else:
                stack.append((child, scope))

    def _direct_bindings(self, scope: Scope) -> None:
        statements = getattr(scope.owner, "body", [])
        if not isinstance(statements, list):
            return
        for statement in statements:
            if isinstance(statement, (ast.Import, ast.ImportFrom)):
                if isinstance(statement, ast.ImportFrom) and statement.level:
                    continue
                for alias in statement.names:
                    local = alias.asname or alias.name.split(".")[0]
                    if scope.bindings[local] != 1 or local in self.declared:
                        continue
                    if isinstance(statement, ast.ImportFrom):
                        path = f"{statement.module}.{alias.name}"
                    else:
                        path = alias.name if alias.asname else local
                    scope.imports[local] = (path, statement.lineno)
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name) and scope.bindings[target.id] == 1:
                        scope.assignments[target.id] = (statement.value, statement.lineno)
            if isinstance(statement, ast.AnnAssign) and statement.value is not None:
                if isinstance(statement.target, ast.Name) and scope.bindings[statement.target.id] == 1:
                    scope.assignments[statement.target.id] = (statement.value, statement.lineno)

    def path(self, call: ast.Call) -> str:
        return self.nodes[call].resolve(call.func, call.lineno)
