"""CRISPR-ASR demo: Shell command risk. Expected: CWE-78 (manual)."""

import subprocess


def check_shell_usage(command):
    return subprocess.run(command, shell=True, check=True)
