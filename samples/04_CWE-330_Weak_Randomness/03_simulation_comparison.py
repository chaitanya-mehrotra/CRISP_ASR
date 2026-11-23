"""CRISPR-ASR demo: Weak randomness. Expected: zero supported findings."""

import random


def roll_dice():
    return random.randint(1, 6)
