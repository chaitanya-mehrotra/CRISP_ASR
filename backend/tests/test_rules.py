import pytest
from fastapi.testclient import TestClient

from app.core.parser import inspect_source
from app.main import app


@pytest.mark.parametrize(
    ("source", "rule_id"),
    [
        ("def read(text):\n    return eval(text)", "CWE-95"),
        ("import subprocess as sp\nsp.run(command, shell=True)", "CWE-78"),
        ("from pickle import loads as read\nread(data)", "CWE-502"),
        ("import random\nsession_token = random.randint(1, 100)", "CWE-330"),
    ],
)
def test_recognized_patterns(source, rule_id):
    finding, = inspect_source(source)["findings"]
    assert finding["id"] == rule_id
    assert finding["fix"]
    assert finding["example"]


@pytest.mark.parametrize(
    "source",
    [
        '# eval(text)\nmessage = "eval(text)"',
        "def calculate(eval):\n    return eval(text)",
        "def example(obj):\n    return obj.eval(text)",
        "import subprocess\nsubprocess.run(['echo', message], shell=False)",
        "import random\nsample = random.randint(0, 100)",
        "import json\njson.loads(text)",
        "import pickle\npickle = adapter\npickle.loads(data)",
    ],
)
def test_ignores_unmatched_patterns(source):
    assert inspect_source(source)["findings"] == []


def test_finding_ranges_match_unicode_editor_columns():
    source = 'marker = "🚀"; eval(text)'
    finding, = inspect_source(source)["findings"]
    assert finding["line"] == 1
    assert finding["column"] == 16
    assert finding["end_column"] == 26


def test_rules_endpoint_matches_checks():
    client = TestClient(app)
    response = client.get("/api/rules")
    assert response.status_code == 200
    assert {rule["id"] for rule in response.json()} == {"CWE-95", "CWE-78", "CWE-502", "CWE-330", "CWE-295", "CWE-327", "CWE-367", "CWE-732"}


@pytest.mark.parametrize(
    ("source", "rule_id"),
    [
        ("import requests as http\nhttp.get(url, verify=False)", "CWE-295"),
        ("from httpx import Client as HTTPClient\nHTTPClient(verify=False)", "CWE-295"),
        ("import ssl\nssl._create_unverified_context()", "CWE-295"),
        ("from hashlib import sha1 as digest\ndigest(data)", "CWE-327"),
        ("import hashlib\nhashlib.new('MD5', data)", "CWE-327"),
        ("from tempfile import mktemp as temp_name\ntemp_name()", "CWE-367"),
        ("import os as fs\nfs.chmod(path, mode=0o666)", "CWE-732"),
    ],
)
def test_additional_rules(source, rule_id):
    finding, = inspect_source(source)["findings"]
    assert finding["id"] == rule_id
    assert finding["repair_mode"] == "manual"
    assert finding["ast_chain"][0] == "Call"
    assert finding["fix"] and finding["question"]


@pytest.mark.parametrize(
    "source",
    [
        "import requests\nrequests.get(url, verify=True)",
        "import requests\nrequests.get(url, verify=trusted_ca)",
        "import hashlib\nhashlib.md5(data, usedforsecurity=False)",
        "import hashlib\nhashlib.sha256(data)",
        "import tempfile\ntempfile.TemporaryFile()",
        "import os\nos.chmod(path, 0o640)",
        "import os\nos.chmod(path, uncertain_mode)",
        "def work(requests):\n    requests.get(url, verify=False)",
    ],
)
def test_additional_rules_skip_safe_or_unresolved_settings(source):
    assert inspect_source(source)["findings"] == []
