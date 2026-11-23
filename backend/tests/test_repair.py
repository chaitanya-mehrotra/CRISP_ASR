from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PREVIEW = "/api/repair-preview"


def get_findings(source):
    response = client.post("/api/parse", json={"source": source})
    assert response.status_code == 200
    return response.json()["findings"]


def request_preview(source, finding):
    return client.post(PREVIEW, json={
        "source": source,
        "rule_id": finding["id"],
        "line": finding["line"],
        "column": finding["column"],
    })


def test_preview_replaces_only_selected_call_and_preserves_formatting():
    source = (
        "import random as r\r\n"
        'marker = "🚀"; session_token = r.choices("ab", k=20)  # retain\r\n'
        'backup_token = r.choice("ab")\r\n'
    )
    first, second = get_findings(source)
    assert first["repairable"] and second["repairable"]
    response = request_preview(source, first)
    assert response.status_code == 200, response.text
    patch = response.json()
    assert patch["source"] == source.replace("r.choices", "r.SystemRandom().choices", 1)
    assert patch["checks"] == {"syntax": True, "compilation": True, "rescan": True}
    assert patch["remaining_findings"] == 1
    assert get_findings(patch["source"])[0]["line"] == second["line"]


def test_other_weaknesses_and_direct_imports_require_manual_review():
    source = "from random import choice\ntoken = choice(values)\nresult = eval(text)\n"
    for finding in get_findings(source):
        assert not finding["repairable"]
        assert request_preview(source, finding).status_code == 409


def test_stale_target_cannot_be_applied():
    source = "import random\ntoken = random.choice(values)"
    finding, = get_findings(source)
    assert request_preview("\n" + source, finding).status_code == 409


def test_compile_rejects_parsable_but_invalid_code():
    source = "import random\nreturn random.choice(values)\ntoken = random.choice(values)"
    finding, = get_findings(source)
    assert request_preview(source, finding).status_code == 422


def test_star_import_and_module_attribute_mutation_block_preview():
    for prefix in ("from local import *\n", "random.SystemRandom = custom_generator\n"):
        source = f"import random\n{prefix}token = random.choice(values)"
        finding, = get_findings(source)
        assert not finding["repairable"]
        assert request_preview(source, finding).status_code == 409


def test_batch_preview_stages_multiple_edits_and_leaves_manual_findings():
    source = (
        "import random\nimport yaml\n"
        "token = random.choice('abc'); nonce = random.getrandbits(32)\n"
        "config = yaml.load(raw)\nrecord = eval(text)\n"
    )
    response = client.post("/api/repair-preview/all", json={"source": source})
    assert response.status_code == 200, response.text
    patch = response.json()
    assert patch["repair_count"] == 3
    assert patch["manual_findings"] == 1
    assert patch["remaining_findings"] == 1
    assert len(patch["changes"]) == 2
    assert [finding["id"] for finding in get_findings(patch["source"])] == ["CWE-95"]


def test_batch_preview_rejects_manual_only_source():
    response = client.post("/api/repair-preview/all", json={"source": "record = eval(text)"})
    assert response.status_code == 409
