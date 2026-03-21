import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# ── Password ────────────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    pwd_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pwd_bytes = plain.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


# ── Access Token (JWT) ───────────────────────────────────────────────────────


def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.access_token_ttl)
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    Raises jwt.InvalidTokenError (→ caught as 401 in dependencies) on failure.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")
    return payload


# ── Refresh Token (opaque) ───────────────────────────────────────────────────


def create_refresh_token(user_id: str) -> str:
    """
    Generate a cryptographically secure random refresh token.
    This is NOT a JWT — it is stored (hashed) in Redis for revocability.
    """
    token_val = secrets.token_urlsafe(64)
    return f"{user_id}::{token_val}"
