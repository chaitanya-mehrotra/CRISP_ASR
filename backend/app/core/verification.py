"""Validate a candidate without executing student code."""

import ast
from collections import Counter

from .rules import find_weaknesses


class RepairValidationError(ValueError):
    pass


def verify_candidate(source: str, original: list[dict], selected: dict | list[dict]) -> dict:
    try:
        tree = ast.parse(source)
        compile(tree, "<repair preview>", "exec", dont_inherit=True)
    except (SyntaxError, ValueError, RecursionError) as error:
        raise RepairValidationError("The candidate did not pass Python syntax and compilation checks.") from error

    remaining = find_weaknesses(tree, source)
    def fingerprint(finding: dict) -> tuple[str, str]:
        return finding["id"], finding["call"]

    before = Counter(map(fingerprint, original))
    actual = Counter(map(fingerprint, remaining))
    if actual - before:
        raise RepairValidationError("Re-scan rejected this candidate because it introduced a new finding.")
    expected = before.copy()
    for finding in selected if isinstance(selected, list) else [selected]:
        expected[fingerprint(finding)] -= 1
    if actual - +expected:
        raise RepairValidationError("Re-scan rejected this candidate because the selected finding stayed flagged.")
    if actual != +expected:
        raise RepairValidationError("Re-scan rejected this candidate because additional findings disappeared.")

    return {
        "checks": {"syntax": True, "compilation": True, "rescan": True},
        "before_findings": len(original),
        "remaining_findings": len(remaining),
        "target_resolved": True,
        "new_findings": 0,
    }
