from __future__ import annotations
import uuid
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from app.config import get_settings

settings = get_settings()


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user_id), "role": role, "type": "access", "iat": now, "exp": now + timedelta(minutes=settings.access_token_expire_minutes)}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user_id), "type": "refresh", "iat": now, "exp": now + timedelta(days=settings.refresh_token_expire_days)}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Not an access token")
    return payload


def decode_refresh_token(token: str) -> dict:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    return payload


def generate_verification_token() -> str:
    return secrets.token_urlsafe(48)
