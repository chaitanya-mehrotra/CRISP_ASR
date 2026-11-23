"""CRISPR-ASR demo: Disabled TLS verification. Expected: CWE-295 (manual)."""

from ssl import _create_unverified_context as create_context


def build_context():
    return create_context()
