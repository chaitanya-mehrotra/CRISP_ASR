import ast
from io import StringIO

from .rules import find_weaknesses
from .verification import verify_candidate


class UnsupportedRepair(ValueError):
    pass


def preview_repair(source: str, rule_id: str, line: int, column: int) -> dict:
    original = find_weaknesses(ast.parse(source), source, include_edits=True)
    selected = next(
        (
            finding for finding in original
            if (finding["id"], finding["line"], finding["column"]) == (rule_id, line, column)
        ),
        None,
    )
    edit = selected["_edit"] if selected else None
    if edit is None:
        raise UnsupportedRepair("No repair template matches this finding in the submitted source.")

    lines = StringIO(source, newline="").readlines()
    before = lines[edit.line - 1]
    after = edit.apply(before)
    lines[edit.line - 1] = after
    patched_source = "".join(lines)

    return {
        "source": patched_source,
        "line": edit.line,
        "before": before.rstrip("\r\n"),
        "after": after.rstrip("\r\n"),
        "explanation": edit.explanation,
        **verify_candidate(patched_source, original, selected),
    }


def preview_available_repairs(source: str) -> dict:
    """Stage non-overlapping template edits and validate the complete candidate."""
    original = find_weaknesses(ast.parse(source), source, include_edits=True)
    supported = [finding for finding in original if finding["_edit"] is not None]
    if not supported:
        raise UnsupportedRepair("These findings require manual review.")

    lines = StringIO(source, newline="").readlines()
    changes = []
    selected = []
    last_line, leftmost = 0, 0
    for finding in sorted(supported, key=lambda item: (item["_edit"].line, -item["_edit"].start)):
        edit = finding["_edit"]
        if edit.line == last_line and edit.end > leftmost:
            continue
        before = lines[edit.line - 1]
        after = edit.apply(before)
        if edit.line != last_line:
            changes.append({
                "line": edit.line,
                "before": before.rstrip("\r\n"),
                "after": after.rstrip("\r\n"),
                "notes": [edit.explanation],
            })
        else:
            changes[-1]["after"] = after.rstrip("\r\n")
            changes[-1]["notes"].append(edit.explanation)
        lines[edit.line - 1] = after
        last_line, leftmost = edit.line, edit.start
        selected.append(finding)

    patched = "".join(lines)
    return {
        "source": patched,
        "changes": changes,
        "repair_count": len(selected),
        "deferred_count": len(supported) - len(selected),
        "manual_findings": len(original) - len(supported),
        **verify_candidate(patched, original, selected),
    }
