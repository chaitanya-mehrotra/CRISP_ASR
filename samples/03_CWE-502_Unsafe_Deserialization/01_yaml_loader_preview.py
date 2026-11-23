"""CRISPR-ASR demo: Unsafe deserialization. Expected: CWE-502 (guided)."""

import yaml as y


def read_config(text):
    return y.load(
        text,  # The expected input is standard YAML data.
    )
