"""CRISPR-ASR demo: Temporary-file race risk. Expected: CWE-367 (manual)."""

from tempfile import mktemp as reserve_name


def report_path():
    return reserve_name(prefix="class_report_")
