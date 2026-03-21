from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Response, status

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


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
    access, refresh = await auth_service.register(body.email, body.username, body.password)
    _set_refresh_cookie(response, refresh)
    return TokenResponse(access_token=access)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response) -> TokenResponse:
    access, refresh = await auth_service.login(body.email, body.password)
    _set_refresh_cookie(response, refresh)
    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response, refresh_token: Optional[str] = Cookie(None)
) -> TokenResponse:
    from app.core.exceptions import UnauthorizedException

    if not refresh_token:
        raise UnauthorizedException("Refresh token missing")

    new_access, new_refresh = await auth_service.refresh(refresh_token)
    _set_refresh_cookie(response, new_refresh)
    return TokenResponse(access_token=new_access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    refresh_token: Optional[str] = Cookie(None),
) -> None:
    await auth_service.logout(str(current_user.id), refresh_token)
    _unset_refresh_cookie(response)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    response: Response,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Revoke all refresh tokens (logout from every device)."""
    await auth_service.logout_all(str(current_user.id))
    _unset_refresh_cookie(response)
