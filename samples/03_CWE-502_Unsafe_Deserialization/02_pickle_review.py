"""CRISPR-ASR demo: Unsafe deserialization. Expected: CWE-502 (manual)."""

from pickle import loads as load_record


def read_legacy_record(data):
    return load_record(data)
