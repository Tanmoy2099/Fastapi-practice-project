from typing import Optional
from fastapi import APIRouter, status, Depends, Response, Cookie

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
)
from app.core.dependencies import get_current_active_user
from app.db.redis import token_store
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        following_count=len(user.following),
        is_active=user.is_active,
    )


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set True in production with HTTPS
        samesite="lax",
        max_age=settings.refresh_token_ttl,
    )


def _unset_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, response: Response) -> TokenResponse:
    if await User.find_one(User.email == body.email):
        raise ConflictException("Email already registered")
    if await User.find_one(User.username == body.username):
        raise ConflictException("Username already taken")

    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    await user.insert()

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    await token_store.store(str(user.id), refresh_token)

    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response) -> TokenResponse:
    user = await User.find_one(User.email == body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise UnauthorizedException("Invalid credentials")
    if not user.is_active:
        raise ForbiddenException("Account is inactive")

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    await token_store.store(str(user.id), refresh_token)

    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response, 
    refresh_token: Optional[str] = Cookie(None)
) -> TokenResponse:
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing")

    try:
        user_id, _ = refresh_token.split("::", 1)
    except ValueError:
        raise UnauthorizedException("Invalid refresh token format")

    if not await token_store.is_valid(user_id, refresh_token):
        raise UnauthorizedException("Invalid or expired refresh token")

    user = await User.get(user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    # Rotate: revoke old, issue new
    await token_store.revoke(user_id, refresh_token)
    new_access = create_access_token(str(user.id), user.role)
    new_refresh = create_refresh_token(str(user.id))
    await token_store.store(user_id, new_refresh)

    _set_refresh_cookie(response, new_refresh)
    return TokenResponse(access_token=new_access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    refresh_token: Optional[str] = Cookie(None),
) -> None:
    if refresh_token:
        await token_store.revoke(str(current_user.id), refresh_token)
    _unset_refresh_cookie(response)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    response: Response,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Revoke all refresh tokens (logout from every device)."""
    await token_store.revoke_all(str(current_user.id))
    _unset_refresh_cookie(response)
