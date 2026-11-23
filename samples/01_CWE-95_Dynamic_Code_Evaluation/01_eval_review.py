"""CRISPR-ASR demo: Dynamic code evaluation. Expected: CWE-95 (manual)."""

def preview_expression(expression):
    return eval(expression)
