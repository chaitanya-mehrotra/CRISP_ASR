"""CRISPR-ASR demo: Disabled TLS verification. Expected: CWE-295 (manual)."""

import requests as http


def fetch_status(url):
    return http.get(url, verify=False, timeout=5).status_code
