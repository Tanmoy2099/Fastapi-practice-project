from typing import List
from app.core.exceptions import ForbiddenException
from app.models.post import Post
from app.models.user import User
from app.repositories.post_repo import post_repo
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.db.redis import cache

_FEED_CACHE_TTL = 60

class PostService:

    def _format_raw_doc(self, doc: dict) -> PostResponse:
        doc["id"] = str(doc.pop("_id"))
        doc["author_id"] = str(doc["author_id"])
        return PostResponse(**doc)

    async def get_by_id(self, post_id: str) -> Post:
        post = await post_repo.get_by_id(post_id)
        if not post:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Post not found")
        return post

    async def get_feed(self, current_user: User) -> List[PostResponse]:
        cache_key = f"feed:{current_user.id}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        if not current_user.following:
            return []

        docs = await post_repo.get_feed(current_user.following)
        result = [self._format_raw_doc(doc) for doc in docs]
        
        serialized = [r.model_dump() for r in result]
        await cache.set(cache_key, serialized, ttl=_FEED_CACHE_TTL)
        return result

    async def get_my_posts(self, author_id: str) -> List[PostResponse]:
        from beanie import PydanticObjectId
        try:
            author_obj_id = PydanticObjectId(author_id)
        except Exception:
            from app.core.exceptions import UnprocessableEntityException
            raise UnprocessableEntityException("Invalid user ID")
            
        docs = await post_repo.get_by_author(author_obj_id)
        return [self._format_raw_doc(doc) for doc in docs]

    async def create(self, data: PostCreate, current_user: User) -> Post:
        post = Post(title=data.title, content=data.content, author_id=current_user.id)
        await post_repo.create(post)
        await cache.delete(f"feed:{current_user.id}")
        return post

    async def update(self, post_id: str, data: PostUpdate, current_user: User) -> Post:
        post = await self.get_by_id(post_id)
        
        if not post.is_owned_by(current_user.id) and not current_user.is_admin():
            raise ForbiddenException("Not your post")

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        return await post_repo.save(post)

    async def delete(self, post_id: str, current_user: User) -> None:
        post = await self.get_by_id(post_id)
        
        if not post.is_owned_by(current_user.id) and not current_user.is_admin():
            raise ForbiddenException("Not your post")
            
        await post_repo.delete(post)

post_service = PostService()
