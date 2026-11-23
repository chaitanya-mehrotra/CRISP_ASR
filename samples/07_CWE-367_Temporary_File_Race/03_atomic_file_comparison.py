"""CRISPR-ASR demo: Temporary-file race risk. Expected: zero supported findings."""

from tempfile import TemporaryFile


def count_bytes(data):
    with TemporaryFile() as handle:
        return handle.write(data)
