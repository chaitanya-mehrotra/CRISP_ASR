"""CRISPR-ASR demo: Dynamic code evaluation. Expected: zero supported findings."""

import json


def read_settings(text):
    return json.loads(text)
