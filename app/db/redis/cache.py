import json
from typing import Any
from app.db.redis.base import BaseRedisStore
from app.core.config import settings


class CacheStore(BaseRedisStore):
    """
    General-purpose async key-value cache with JSON serialization.

    Use for: post feeds, user profiles, expensive aggregations.

    Usage:
        from app.db.redis import cache
        await cache.set("feed:user_id", posts_list, ttl=300)
        data = await cache.get("feed:user_id")
    """

    def __init__(self) -> None:
        super().__init__(db=settings.redis_db)

    @staticmethod
    def _serialize(value: Any) -> str:
        return json.dumps(value, default=str)

    @staticmethod
    def _deserialize(raw: str) -> Any:
        return json.loads(raw)

    async def get(self, key: str) -> Any | None:
        raw = await self.client.get(key)
        return self._deserialize(raw) if raw is not None else None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else settings.redis_cache_ttl
        await self.client.set(key, self._serialize(value), ex=ttl)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def clear_prefix(self, prefix: str) -> int:
        keys = await self.client.keys(f"{prefix}*")
        return await self.client.delete(*keys) if keys else 0


cache = CacheStore()
