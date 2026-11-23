import ast

import pytest
from fastapi.testclient import TestClient

from app.core.parser import inspect_source
from app.core.verification import RepairValidationError, verify_candidate
from app.main import app

client = TestClient(app)


def scan(source):
    return inspect_source(source)["findings"]


def preview(source, finding):
    return client.post("/api/repair-preview", json={
        "source": source, "rule_id": finding["id"],
        "line": finding["line"], "column": finding["column"],
    })


def test_aliases_resolve_per_scope_and_ignore_parameter_shadow():
    source = """import subprocess as sp
def shadowed(sp, value):
    return sp.run(value, shell=True)

def real(value):
    import subprocess as runner
    return runner.run(value, shell=True)
"""
    finding, = scan(source)
    assert finding["line"] == 7
    assert finding["ast_chain"] == ["Call", "Attribute", "Name"]
    assert "Function parameter: value" in finding["origin"]


def test_local_simple_assignment_traces_input():
    finding, = scan("data = input()\nresult = eval(data)")
    assert finding["origin"] == "Local input source: builtins.input() on line 1."
    assert finding["repair_mode"] == "manual"


def test_scope_shadow_does_not_hide_valid_module_call():
    source = "from random import choice as pick\ndef skip(pick):\n    return pick('ab')\ntoken = pick('ab')"
    finding, = scan(source)
    assert finding["line"] == 4
    assert finding["repair_mode"] == "manual"


@pytest.mark.parametrize("source", [
    "import random\nvalues = [random.choice('ab') for _ in range(2)]",
    "import random\nlot = [random.choice('ab') for random in providers]",
    "import yaml as y\nfrom yaml import SafeLoader as Safe\ny.load(text, Loader=Safe)",
    "import yaml as y\ny.safe_load(text)",
])
def test_safe_or_unresolved_calls(source):
    assert scan(source) == []


@pytest.mark.parametrize("source, path", [
    ("compile(text, '<string>', 'exec')", "builtins.compile"),
    ("__import__(name)", "builtins.__import__"),
    ("import os as platform_os\nplatform_os.popen(command)", "os.popen"),
    ("from marshal import loads as load\nload(data)", "marshal.loads"),
    ("from cPickle import loads\nloads(data)", "cPickle.loads"),
    ("import random\nconfigure(apiKey=random.getrandbits(64))", "random.getrandbits"),
])
def test_expanded_detection(source, path):
    finding, = scan(source)
    assert finding["call"] == path


def test_multiline_yaml_preview_preserves_comments_and_arguments():
    source = "import yaml as y\nconfig = y.load(\n    raw,  # retain\n)\n"
    finding, = scan(source)
    assert (finding["line"], finding["column"], finding["end_line"], finding["end_column"]) == (2, 10, 4, 2)
    assert finding["repair_mode"] == "guided"
    result = preview(source, finding)
    assert result.status_code == 200, result.text
    assert result.json()["source"] == source.replace("y.load", "y.safe_load")
    assert result.json()["before_findings"] == 1
    assert result.json()["target_resolved"]
    assert result.json()["new_findings"] == 0


def test_shell_preview_is_limited_to_fixed_plain_posix_commands():
    source = "import subprocess as sp\nsp.run('/usr/bin/printf hello', shell=True, check=True)"
    finding, = scan(source)
    result = preview(source, finding)
    patch = result.json()
    assert result.status_code == 200, patch
    assert patch["after"] == "sp.run(['/usr/bin/printf', 'hello'], shell=False, check=True)"
    assert "POSIX-only" in patch["explanation"]
    for command in ("'printf hello'", "'/usr/bin/printf hello > output'", 'command',
                    "'/usr/bin/printf hello', cwd=workdir"):
        manual = f"import subprocess\nsubprocess.run({command}, shell=True)"
        only, = scan(manual)
        assert only["repair_mode"] == "manual"


def test_verifier_rejects_new_or_unresolved_findings():
    original = scan("import yaml\nyaml.load(raw)")
    for candidate in ("eval(data)", "import yaml\nyaml.load(raw)"):
        ast.parse(candidate)
        with pytest.raises(RepairValidationError, match="Re-scan rejected"):
            verify_candidate(candidate, original, original[0])


def test_breakdown_counts_major_constructs():
    summary = inspect_source("import json\nclass Config:\n def read(self):\n  if ready:\n   return json.loads(text)")
    assert summary["structure"] == {"functions": 1, "classes": 1, "imports": 1, "calls": 1, "branches": 1}
