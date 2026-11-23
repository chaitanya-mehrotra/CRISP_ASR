"""CRISPR-ASR demo: Shell command risk. Expected: zero supported findings."""

import subprocess
import sys


def python_version():
    return subprocess.run([sys.executable, "--version"], shell=False, check=True)
