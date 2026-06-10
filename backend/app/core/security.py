import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.config import settings

API_KEY_PREFIX = "apk_"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: UUID, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(hours=settings.jwt_expire_hours))
    payload: dict[str, Any] = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return UUID(payload["sub"])
    except (JWTError, ValueError, KeyError) as exc:
        raise ValueError("Invalid token") from exc


def is_api_key(token: str) -> bool:
    return token.startswith(API_KEY_PREFIX)


def generate_api_key() -> tuple[str, str, str]:
    """Return (full_key, key_prefix, key_hash)."""
    secret = secrets.token_urlsafe(32)
    full_key = f"{API_KEY_PREFIX}{secret}"
    key_prefix = full_key[:12]
    key_hash = hash_api_key(full_key)
    return full_key, key_prefix, key_hash


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
