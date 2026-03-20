import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.db.redis import permission_store
from app.models.user import User

_bearer = HTTPBearer()


# ── Token extraction ─────────────────────────────────────────────────────────

async def _get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    try:
        return decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ── Current user ─────────────────────────────────────────────────────────────

async def get_current_user(
    payload: dict = Depends(_get_token_payload),
) -> User:
    user = await User.get(payload["sub"])
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    return current_user


# ── Role-based access control ─────────────────────────────────────────────────

def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    Checks PermissionStore (Redis) first, falls back to DB on cache miss.

    Usage:
        @router.delete("/{id}", dependencies=[Depends(require_role("admin"))])
    """
    async def _check(
        payload: dict = Depends(_get_token_payload),
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        user_id = str(current_user.id)

        # 1. Try Redis cache first
        cached_role = await permission_store.get(user_id)
        if cached_role is None:
            # 2. Cache miss — load from DB and cache it
            cached_role = current_user.role
            await permission_store.set(user_id, cached_role)

        if cached_role != required_role:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"Requires '{required_role}' role",
            )
        return current_user

    return _check
