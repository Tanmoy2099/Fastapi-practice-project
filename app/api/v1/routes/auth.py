from fastapi import APIRouter, HTTPException, status, Depends

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.core.dependencies import get_current_active_user
from app.db.redis import token_store
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, LogoutRequest, TokenResponse
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


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate) -> TokenResponse:
    if await User.find_one(User.email == body.email):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    if await User.find_one(User.username == body.username):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Username already taken")

    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    await user.insert()

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token()
    await token_store.store(str(user.id), refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    user = await User.find_one(User.email == body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token()
    await token_store.store(str(user.id), refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest) -> TokenResponse:
    # Refresh token is opaque — we must find the user ID it belongs to.
    # We store tokens as: rt:{user_id}:{hash} so we scan to find the owner.
    # Better UX: caller also provides user_id. We require it via the query param.
    # Actually cleaner: embed user_id inside the refresh token payload as prefix.
    # Here we store user_id alongside the token on issue and return it.
    # For simplicity: accept user_id from caller and validate the pair.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use /auth/refresh/{user_id} with your refresh token",
    )


@router.post("/refresh/{user_id}", response_model=TokenResponse)
async def refresh_token(user_id: str, body: RefreshRequest) -> TokenResponse:
    if not await token_store.is_valid(user_id, body.refresh_token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = await User.get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    # Rotate: revoke old, issue new
    await token_store.revoke(user_id, body.refresh_token)
    new_access = create_access_token(str(user.id), user.role)
    new_refresh = create_refresh_token()
    await token_store.store(user_id, new_refresh)

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: LogoutRequest,
    current_user: User = Depends(get_current_active_user),
) -> None:
    await token_store.revoke(str(current_user.id), body.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Revoke all refresh tokens (logout from every device)."""
    await token_store.revoke_all(str(current_user.id))
