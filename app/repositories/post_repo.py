from typing import List, Optional

from beanie import PydanticObjectId

from app.models.post import Post


class PostRepository:
    """Encapsulates all database operations for the Post model."""

    async def get_by_id(self, post_id: str | PydanticObjectId) -> Optional[Post]:
        if isinstance(post_id, str):
            try:
                post_id = PydanticObjectId(post_id)
            except Exception:
                return None
        return await Post.get(post_id)

    async def create(self, post: Post) -> Post:
        return await post.insert()

    async def save(self, post: Post) -> Post:
        return await post.save()

    async def delete(self, post: Post) -> None:
        await post.delete()

    async def get_feed(self, following_ids: List[PydanticObjectId]) -> List[dict]:
        """Returns raw dictionaries from aggregation pipeline to bypass Beanie limitations."""
        pipeline = [
            {"$match": {"author_id": {"$in": following_ids}, "published": True}},
            {"$sort": {"created_at": -1}},
        ]
        cursor = Post.get_pymongo_collection().aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_by_author(self, author_id: PydanticObjectId) -> List[dict]:
        pipeline = [{"$match": {"author_id": author_id}}, {"$sort": {"created_at": -1}}]
        cursor = Post.get_pymongo_collection().aggregate(pipeline)
        return await cursor.to_list(length=None)


post_repo = PostRepository()
