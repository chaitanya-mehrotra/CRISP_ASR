"""Local account and session storage for the classroom prototype."""

import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, SecretStr

router = APIRouter(prefix="/api/auth", tags=["Local accounts"])
DATABASE = Path(__file__).resolve().parents[1] / "accounts.sqlite3"
COOKIE = "crispr_session"
SESSION_SECONDS = 8 * 60 * 60
ITERATIONS = 600_000
USERNAME = re.compile(r"[a-z0-9_-]{3,32}")


class Credentials(BaseModel):
    username: str = ""
    password: SecretStr = SecretStr("")


class Account(BaseModel):
    username: str


@contextmanager
def database():
    connection = sqlite3.connect(DATABASE)
    try:
        with connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS accounts ("
                "username TEXT PRIMARY KEY, salt BLOB NOT NULL, password_hash BLOB NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS sessions ("
                "digest TEXT PRIMARY KEY, username TEXT NOT NULL REFERENCES accounts(username), "
                "expires INTEGER NOT NULL)"
            )
            yield connection
    finally:
        connection.close()


def password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)


def digest_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def set_session(response: Response, request: Request, username: str) -> Account:
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with database() as connection:
        connection.execute("DELETE FROM sessions WHERE expires <= ?", (now,))
        previous = request.cookies.get(COOKIE)
        if previous:
            connection.execute("DELETE FROM sessions WHERE digest = ?", (digest_token(previous),))
        connection.execute(
            "INSERT INTO sessions VALUES (?, ?, ?)",
            (digest_token(token), username, now + SESSION_SECONDS),
        )
    response.set_cookie(
        COOKIE, token, max_age=SESSION_SECONDS, httponly=True,
        secure=request.url.scheme == "https", samesite="strict", path="/api/auth",
    )
    response.headers["Cache-Control"] = "no-store"
    return Account(username=username)


@router.post("/register", status_code=201)
def register(credentials: Credentials, request: Request, response: Response) -> Account:
    name = credentials.username.strip().lower()
    password = credentials.password.get_secret_value()
    if not USERNAME.fullmatch(name):
        raise HTTPException(422, "Use 3–32 letters, numbers, underscores, or hyphens for your username.")
    if not 12 <= len(password) <= 128:
        raise HTTPException(422, "Choose a password between 12 and 128 characters.")
    salt = secrets.token_bytes(16)
    hashed = password_hash(password, salt)
    try:
        with database() as connection:
            connection.execute("INSERT INTO accounts VALUES (?, ?, ?)", (name, salt, hashed))
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "That username is already in use.") from error
    return set_session(response, request, name)


@router.post("/login")
def login(credentials: Credentials, request: Request, response: Response) -> Account:
    name = credentials.username.strip().lower()
    password = credentials.password.get_secret_value()
    if not USERNAME.fullmatch(name) or not 12 <= len(password) <= 128:
        raise HTTPException(401, "Incorrect username or password.")
    with database() as connection:
        account = connection.execute(
            "SELECT salt, password_hash FROM accounts WHERE username = ?", (name,)
        ).fetchone()
    salt, stored_hash = account or (b"\x00" * 16, b"\x00" * 32)
    if not hmac.compare_digest(password_hash(password, salt), stored_hash) or not account:
        raise HTTPException(401, "Incorrect username or password.")
    return set_session(response, request, name)


@router.get("/session")
def session(request: Request, response: Response) -> Account | None:
    response.headers["Cache-Control"] = "no-store"
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    with database() as connection:
        row = connection.execute(
            "SELECT username FROM sessions WHERE digest = ? AND expires > ?",
            (digest_token(token), int(time.time())),
        ).fetchone()
    return Account(username=row[0]) if row else None


@router.post("/logout", status_code=204)
def logout(request: Request) -> Response:
    token = request.cookies.get(COOKIE)
    if token:
        with database() as connection:
            connection.execute("DELETE FROM sessions WHERE digest = ?", (digest_token(token),))
    response = Response(status_code=204, headers={"Cache-Control": "no-store"})
    response.delete_cookie(COOKIE, path="/api/auth", httponly=True, samesite="strict")
    return response
