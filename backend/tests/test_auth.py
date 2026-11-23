import sqlite3

from fastapi.testclient import TestClient

from app import auth
from app.main import app


def test_local_account_and_session(tmp_path, monkeypatch):
    location = tmp_path / "accounts.sqlite3"
    monkeypatch.setattr(auth, "DATABASE", location)
    client = TestClient(app)
    password = "example classroom password"
    creds = {"username": "Student_1", "password": password}

    assert client.get("/api/auth/session").json() is None
    assert client.post("/api/parse", json={"source": "x = 1"}).status_code == 200
    registered = client.post("/api/auth/register", json=creds)
    assert registered.status_code == 201
    assert registered.json() == {"username": "student_1"}
    assert "HttpOnly" in registered.headers["set-cookie"]
    assert "SameSite=strict" in registered.headers["set-cookie"]
    token = registered.cookies[auth.COOKIE]
    with sqlite3.connect(location) as connection:
        stored = connection.execute("SELECT password_hash FROM accounts").fetchone()[0]
        digest = connection.execute("SELECT digest FROM sessions").fetchone()[0]
    assert stored != password.encode()
    assert digest == auth.digest_token(token)
    assert client.get("/api/auth/session").json() == {"username": "student_1"}
    assert client.post("/api/auth/register", json=creds).status_code == 409
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/session", cookies={auth.COOKIE: token}).json() is None
    assert client.post("/api/auth/login", json={**creds, "password": "incorrect password"}).status_code == 401
    assert client.post("/api/auth/login", json=creds).status_code == 200

    with sqlite3.connect(location) as connection:
        connection.execute("UPDATE sessions SET expires = 0")
    assert client.get("/api/auth/session").json() is None


def test_invalid_registration_does_not_echo_password():
    client = TestClient(app)
    response = client.post("/api/auth/register", json={"username": [], "password": "test-only-secret"})
    assert response.status_code == 422
    assert "test-only-secret" not in response.text
