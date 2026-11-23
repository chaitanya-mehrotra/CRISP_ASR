"""CRISPR-ASR demo: Weak hashing. Expected: zero supported findings."""

import hashlib


def artifact_digest(data):
    return hashlib.sha256(data).hexdigest()
