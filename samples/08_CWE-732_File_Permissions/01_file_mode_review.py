"""CRISPR-ASR demo: World-writable POSIX permissions. Expected: CWE-732 (manual)."""

import os


def update_report_mode(path):
    os.chmod(path, 0o666)
