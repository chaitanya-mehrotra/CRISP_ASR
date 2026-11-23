"""CRISPR-ASR demo: Weak randomness. Expected: CWE-330 (preview)."""

import random as rng
import string

ALPHABET = string.ascii_letters + string.digits


def make_session_token():
    return "".join(rng.choices(ALPHABET, k=24))
