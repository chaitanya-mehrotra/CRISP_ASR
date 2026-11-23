"""CRISPR-ASR demo: Temporary-file race risk. Expected: CWE-367 (manual)."""

import tempfile


def draft_path():
    return tempfile.mktemp(suffix=".txt")
