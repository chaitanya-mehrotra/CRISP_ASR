"""CRISPR-ASR demo: Weak hashing. Expected: CWE-327 (manual)."""

import hashlib


def artifact_digest(data):
    return hashlib.sha1(data).hexdigest()
