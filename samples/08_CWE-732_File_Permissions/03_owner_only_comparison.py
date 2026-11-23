"""CRISPR-ASR demo: World-writable POSIX permissions. Expected: zero supported findings."""

import os


def make_report_private(path):
    os.chmod(path, 0o600)
