"""Artifact report classroom fixture. Importing this file fetches nothing."""

import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit

import requests


MAX_DOWNLOAD_BYTES = 2_000_000


@dataclass(frozen=True)
class Artifact:
    label: str
    url: str


@dataclass(frozen=True)
class ArtifactReport:
    label: str
    byte_count: int
    algorithm: str
    digest: str


def build_artifact(label: str, url: str) -> Artifact:
    if not label.strip():
        raise ValueError("An artifact label is required")
    address = urlsplit(url)
    if address.scheme != "https" or not address.hostname:
        raise ValueError("An HTTPS URL is required")
    return Artifact(label.strip(), url)


def download_artifact(artifact: Artifact) -> bytes:
    chunks = []
    size = 0
    with requests.get(artifact.url, verify=True, timeout=5, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8192):
            size += len(chunk)
            if size > MAX_DOWNLOAD_BYTES:
                raise ValueError("The artifact exceeds the size limit")
            chunks.append(chunk)
    return b"".join(chunks)


def create_report(artifact: Artifact, content: bytes) -> ArtifactReport:
    digest = hashlib.sha256(content).hexdigest()
    return ArtifactReport(artifact.label, len(content), "sha256", digest)


def render_report(report: ArtifactReport) -> str:
    return json.dumps(asdict(report), indent=2, sort_keys=True) + "\n"


def save_report(report: ArtifactReport, destination: Path) -> Path:
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(render_report(report))
    return destination


def show_completion_banner() -> str:
    """Optional POSIX banner used in a lab demonstration."""
    completed = subprocess.run(["/usr/bin/printf", "Report-ready"], shell=False, check=True, capture_output=True, text=True)
    return completed.stdout


def prepare_artifact_report(label: str, url: str, destination: Path) -> ArtifactReport:
    artifact = build_artifact(label, url)
    content = download_artifact(artifact)
    report = create_report(artifact, content)
    save_report(report, destination)
    return report
