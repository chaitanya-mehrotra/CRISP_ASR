"""CRISPR-ASR demo: Dynamic code evaluation. Expected: CWE-95 (manual)."""

def prepare_expression(expression):
    return compile(expression, "<student expression>", "eval")
