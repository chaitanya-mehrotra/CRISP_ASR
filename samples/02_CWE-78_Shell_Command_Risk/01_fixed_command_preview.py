"""CRISPR-ASR demo: Shell command risk. Expected: CWE-78 (guided)."""

import subprocess as sp


def display_message():
    return sp.run("/usr/bin/printf hello", shell=True, check=True)
