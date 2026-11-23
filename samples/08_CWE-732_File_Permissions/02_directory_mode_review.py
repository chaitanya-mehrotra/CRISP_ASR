"""CRISPR-ASR demo: World-writable POSIX permissions. Expected: CWE-732 (manual)."""

from os import chmod as set_mode


def update_directory_mode(path):
    set_mode(path, mode=0o777)
