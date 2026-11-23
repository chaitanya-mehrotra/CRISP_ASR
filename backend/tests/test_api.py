from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_parse_reports_real_ast():
    response = client.post("/api/parse", json={"source": "print(1)"})
    assert response.status_code == 200
    assert response.json()["node_types"]["Call"] == 1
    assert response.json()["top_level"] == ["Expr"]


def test_invalid_syntax_reports_location():
    response = client.post("/api/parse", json={"source": "if True\n    pass"})
    assert response.status_code == 422
    assert response.json()["detail"]["line"] == 1


def test_rejects_oversized_source():
    response = client.post("/api/parse", json={"source": " " * 100_001})
    assert response.status_code == 422


def test_outline_reports_named_statements_and_source_lines():
    source = 'import json\n\nclass Config:\n    pass\n\nprint("ready")'
    response = client.post("/api/parse", json={"source": source})
    assert response.status_code == 200
    assert response.json()["outline"] == [
        {"kind": "Import", "name": None, "line": 1},
        {"kind": "ClassDef", "name": "Config", "line": 3},
        {"kind": "Expr", "name": None, "line": 6},
    ]
