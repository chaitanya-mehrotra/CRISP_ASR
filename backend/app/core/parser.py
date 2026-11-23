import ast
from collections import Counter

from .rules import find_weaknesses


def inspect_source(source: str) -> dict:
    tree = ast.parse(source)
    counts = Counter(type(node).__name__ for node in ast.walk(tree))
    return {
        "node_count": counts.total(),
        "structure": {
            "functions": counts["FunctionDef"] + counts["AsyncFunctionDef"],
            "classes": counts["ClassDef"],
            "imports": counts["Import"] + counts["ImportFrom"],
            "calls": counts["Call"],
            "branches": sum(counts[kind] for kind in ("If", "IfExp", "Match", "ExceptHandler")),
        },
        "node_types": dict(sorted(counts.items())),
        "findings": find_weaknesses(tree, source),
        "top_level": [type(node).__name__ for node in tree.body],
        "outline": [
            {
                "kind": type(node).__name__,
                "name": getattr(node, "name", None),
                "line": node.lineno,
            }
            for node in tree.body
        ],
    }
