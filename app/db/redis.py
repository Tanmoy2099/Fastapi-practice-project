import json
from typing import Any
import redis.asyncio as aioredis
from app.core.config import settings


class RedisCache:
    """
    Async Redis cache wrapper.

    Usage:
        cache = RedisCache()
        await cache.connect()

        await cache.set("key", {"foo": "bar"})
        data = await cache.get("key")
        await cache.delete("key")

        await cache.close()
    """

    def __init__(self) -> None:
        self._client: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Open the Redis connection pool."""
        self._client = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
        )

    async def close(self) -> None:
        """Close the Redis connection pool."""
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── Core helpers ────────────────────────────────────────────────────

    def _ensure_connected(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("RedisCache is not connected. Call connect() first.")
        return self._client

    @staticmethod
    def _serialize(value: Any) -> str:
        return json.dumps(value)

    @staticmethod
    def _deserialize(value: str) -> Any:
        return json.loads(value)

    # ── Public API ──────────────────────────────────────────────────────

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Cache a value. TTL defaults to settings.redis_cache_ttl."""
        client = self._ensure_connected()
        ttl = ttl if ttl is not None else settings.redis_cache_ttl
        await client.set(key, self._serialize(value), ex=ttl)

    async def get(self, key: str) -> Any | None:
        """Return cached value or None if missing / expired."""
        client = self._ensure_connected()
        raw = await client.get(key)
        return self._deserialize(raw) if raw is not None else None

    async def delete(self, key: str) -> None:
        """Remove a key from the cache."""
        client = self._ensure_connected()
        await client.delete(key)

    async def exists(self, key: str) -> bool:
        """Return True if the key exists in the cache."""
        client = self._ensure_connected()
        return bool(await client.exists(key))

    async def clear_prefix(self, prefix: str) -> int:
        """Delete all keys matching a prefix pattern. Returns count deleted."""
        client = self._ensure_connected()
        keys = await client.keys(f"{prefix}*")
        if keys:
            return await client.delete(*keys)
        return 0


# Singleton instance — imported and shared across the app
cache = RedisCache()
