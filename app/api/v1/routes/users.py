from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserProfile, UserResponse
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        following_count=len(user.following),
        is_active=user.is_active,
    )


def _to_profile(user: User) -> UserProfile:
    return UserProfile(
        id=str(user.id),
        username=user.username,
        following_count=len(user.following),
    )


# ── Profile ───────────────────────────────────────────────────────────────────


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    return _to_response(current_user)


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str) -> UserProfile:
    user = await user_service.get_by_id(user_id)
    return _to_profile(user)


# ── Follow / Unfollow ─────────────────────────────────────────────────────────


@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    await user_service.follow(current_user, user_id)


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    await user_service.unfollow(current_user, user_id)


# ── Follow lists ──────────────────────────────────────────────────────────────


@router.get("/{user_id}/following", response_model=list[UserProfile])
async def get_following(user_id: str) -> list[UserProfile]:
    following_users = await user_service.get_following(user_id)
    return [_to_profile(u) for u in following_users]


@router.get("/{user_id}/followers", response_model=list[UserProfile])
async def get_followers(user_id: str) -> list[UserProfile]:
    followers = await user_service.get_followers(user_id)
    return [_to_profile(u) for u in followers]
