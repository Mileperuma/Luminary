"""Password hashing and JWT issue/verify helpers.

Uses `bcrypt` directly (passlib is unmaintained and incompatible with
modern bcrypt). The 72-byte input limit that bcrypt enforces is handled
here by truncating; for portfolio-scale passwords this is fine, and it
matches the behaviour of Django and Flask-Security.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

_BCRYPT_MAX_INPUT_BYTES = 72


def _to_bcrypt_bytes(value: str) -> bytes:
    """Encode + truncate to bcrypt's 72-byte limit."""
    return value.encode("utf-8")[:_BCRYPT_MAX_INPUT_BYTES]


# ---------- passwords ----------

def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(_to_bcrypt_bytes(plain), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bcrypt_bytes(plain), hashed.encode("utf-8"))
    except ValueError:
        # malformed hash on disk — treat as a failed verification
        return False


# ---------- JWT ----------

def create_access_token(user_id: UUID, expires_minutes: int | None = None) -> str:
    exp = datetime.now(UTC) + timedelta(
        minutes=expires_minutes if expires_minutes is not None else settings.JWT_EXPIRES_MINUTES
    )
    payload = {"sub": str(user_id), "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class InvalidTokenError(Exception):
    """Raised when a JWT fails to decode or its claims don't match expectations."""


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise InvalidTokenError("token signature or expiry invalid") from exc

    sub = payload.get("sub")
    if not sub:
        raise InvalidTokenError("token missing subject")
    try:
        return UUID(sub)
    except ValueError as exc:
        raise InvalidTokenError("subject is not a valid UUID") from exc
