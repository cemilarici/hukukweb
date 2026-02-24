from __future__ import annotations

import secrets
from datetime import UTC, datetime

from argon2 import PasswordHasher
from fastapi import Depends, Form, HTTPException, Request, status

from app.config import DATA_DIR, settings
from app.models import UserRecord
from app.storage import read_json, write_json_atomic

ADMIN_SESSION_KEY = "admin_user"
CSRF_SESSION_KEY = "csrf_token"

_hasher = PasswordHasher()


def _admin_path():
    return DATA_DIR / "users" / "admin.json"


def ensure_admin_user() -> None:
    path = _admin_path()
    if path.exists():
        return
    now = datetime.now(UTC)
    record = UserRecord(
        username=settings.admin_username,
        password_hash=_hasher.hash(settings.admin_password),
        created_at=now,
        updated_at=now,
    )
    write_json_atomic(path, record.model_dump(mode="json"))


def verify_login(username: str, password: str) -> bool:
    raw = read_json(_admin_path(), default=None)
    if not raw:
        return False
    record = UserRecord(**raw)
    if record.username != username:
        return False
    try:
        return _hasher.verify(record.password_hash, password)
    except Exception:
        return False


def login_admin(request: Request, username: str) -> None:
    request.session[ADMIN_SESSION_KEY] = username


def logout_admin(request: Request) -> None:
    request.session.pop(ADMIN_SESSION_KEY, None)


def get_current_admin(request: Request) -> str:
    username = request.session.get(ADMIN_SESSION_KEY)
    if not username:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})
    return str(username)


def issue_csrf(request: Request) -> str:
    token = request.session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        request.session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf(request: Request, token: str) -> None:
    expected = request.session.get(CSRF_SESSION_KEY)
    if not expected or not token or expected != token:
        raise HTTPException(status_code=400, detail="Geçersiz CSRF token")


def csrf_form_token(csrf_token: str = Form(...)) -> str:
    return csrf_token


def require_admin(_: str = Depends(get_current_admin)) -> None:
    return None
