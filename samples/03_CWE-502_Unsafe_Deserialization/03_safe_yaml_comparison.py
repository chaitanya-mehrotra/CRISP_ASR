"""CRISPR-ASR demo: Unsafe deserialization. Expected: zero supported findings."""

import yaml


def read_config(text):
    return yaml.safe_load(text)
