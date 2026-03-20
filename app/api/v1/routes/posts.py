from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_active_user, require_role
from app.db.redis import cache
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse

router = APIRouter(prefix="/posts", tags=["Posts"])

_FEED_CACHE_TTL = 60  # seconds


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


async def _get_post_or_404(post_id: str) -> Post:
    try:
        obj_id = PydanticObjectId(post_id)
    except Exception:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid post ID")
    post = await Post.get(obj_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


# ── Feed (posts from followed users) ──────────────────────────────────────────

@router.get("/feed", response_model=list[PostResponse])
async def get_feed(
    current_user: User = Depends(get_current_active_user),
) -> list[PostResponse]:
    cache_key = f"feed:{current_user.id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    if not current_user.following:
        return []

    posts = await Post.find(
        Post.author_id.in_(current_user.following),  # type: ignore[attr-defined]
        Post.published == True,
    ).sort(-Post.created_at).to_list()

    result = [_to_response(p) for p in posts]
    serialized = [r.model_dump() for r in result]
    await cache.set(cache_key, serialized, ttl=_FEED_CACHE_TTL)
    return result


# ── Own posts ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[PostResponse])
async def get_my_posts(
    current_user: User = Depends(get_current_active_user),
) -> list[PostResponse]:
    posts = await Post.find(Post.author_id == current_user.id).sort(-Post.created_at).to_list()
    return [_to_response(p) for p in posts]


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostCreate,
    current_user: User = Depends(get_current_active_user),
) -> PostResponse:
    post = Post(title=body.title, content=body.content, author_id=current_user.id)
    await post.insert()
    await cache.delete(f"feed:{current_user.id}")  # invalidate own followers' feed
    return _to_response(post)


# ── Update ────────────────────────────────────────────────────────────────────

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    body: PostUpdate,
    current_user: User = Depends(get_current_active_user),
) -> PostResponse:
    post = await _get_post_or_404(post_id)

    if not post.is_owned_by(current_user.id) and not current_user.is_admin():
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not your post")

    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await post.save()
    return _to_response(post)


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    post = await _get_post_or_404(post_id)

    if not post.is_owned_by(current_user.id) and not current_user.is_admin():
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not your post")

    await post.delete()
