"""CRISPR-ASR demo: Weak randomness. Expected: CWE-330 (preview)."""

import random


def make_nonce():
    return random.getrandbits(128)
