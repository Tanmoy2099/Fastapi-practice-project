from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_active_user
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services.post_service import post_service

router = APIRouter(prefix="/posts", tags=["Posts"])


def _to_response(post: Post) -> PostResponse:
    return PostResponse(
        id=str(post.id),
        title=post.title,
        content=post.content,
        published=post.published,
        author_id=str(post.author_id),
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


# ── Feed (posts from followed users) ──────────────────────────────────────────

@router.get("/feed", response_model=list[PostResponse])
async def get_feed(
    current_user: User = Depends(get_current_active_user),
) -> list[PostResponse]:
    return await post_service.get_feed(current_user)


# ── Own posts ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[PostResponse])
async def get_my_posts(
    current_user: User = Depends(get_current_active_user),
) -> list[PostResponse]:
    return await post_service.get_my_posts(str(current_user.id))


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostCreate,
    current_user: User = Depends(get_current_active_user),
) -> PostResponse:
    post = await post_service.create(body, current_user)
    return _to_response(post)


# ── Read Single ───────────────────────────────────────────────────────────────

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user),
) -> PostResponse:
    post = await post_service.get_by_id(post_id)
    return _to_response(post)


# ── Update ────────────────────────────────────────────────────────────────────

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    body: PostUpdate,
    current_user: User = Depends(get_current_active_user),
) -> PostResponse:
    post = await post_service.update(post_id, body, current_user)
    return _to_response(post)


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    await post_service.delete(post_id, current_user)
