"""CRISPR-ASR demo: Weak hashing. Expected: CWE-327 (manual)."""

from hashlib import new as make_hash


def artifact_digest(data):
    return make_hash("md5", data).hexdigest()
