"""CRISPR-ASR demo: Disabled TLS verification. Expected: zero supported findings."""

import ssl


def build_context():
    return ssl.create_default_context()
