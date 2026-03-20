from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserProfile

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


async def _get_user_or_404(user_id: str) -> User:
    try:
        obj_id = PydanticObjectId(user_id)
    except Exception:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    user = await User.get(obj_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    return _to_response(current_user)


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str) -> UserProfile:
    user = await _get_user_or_404(user_id)
    return _to_profile(user)


# ── Follow / Unfollow ─────────────────────────────────────────────────────────

@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    target = await _get_user_or_404(user_id)

    if target.id == current_user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    if current_user.follows(target.id):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Already following this user")

    current_user.following.append(target.id)
    await current_user.save()


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    target = await _get_user_or_404(user_id)

    if not current_user.follows(target.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not following this user")

    current_user.following.remove(target.id)
    await current_user.save()


# ── Follow lists ──────────────────────────────────────────────────────────────

@router.get("/{user_id}/following", response_model=list[UserProfile])
async def get_following(user_id: str) -> list[UserProfile]:
    user = await _get_user_or_404(user_id)
    following_users = await User.find(
        {"_id": {"$in": user.following}}
    ).to_list()
    return [_to_profile(u) for u in following_users]


@router.get("/{user_id}/followers", response_model=list[UserProfile])
async def get_followers(user_id: str) -> list[UserProfile]:
    target = await _get_user_or_404(user_id)
    followers = await User.find(
        {"following": target.id}
    ).to_list()
    return [_to_profile(u) for u in followers]
