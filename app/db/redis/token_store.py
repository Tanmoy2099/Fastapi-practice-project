import hashlib

from app.core.config import settings
from app.db.redis.base import BaseRedisStore


class TokenStore(BaseRedisStore):
    """
    Refresh token lifecycle management.

    Tokens are stored by a SHA-256 hash of the raw token string,
    not the token itself, so Redis never holds plaintext tokens.

    Key pattern: rt:{user_id}:{sha256(token)}
    TTL: settings.refresh_token_ttl (default 7 days)

    Usage:
        from app.db.redis import token_store
        await token_store.store(user_id, refresh_token)
        valid = await token_store.is_valid(user_id, refresh_token)
        await token_store.revoke(user_id, refresh_token)
        await token_store.revoke_all(user_id)   # logout everywhere
    """

    def __init__(self) -> None:
        super().__init__(db=settings.redis_db)

    @staticmethod
    def _key(user_id: str, token: str) -> str:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return f"rt:{user_id}:{token_hash}"

    async def store(self, user_id: str, token: str, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else settings.refresh_token_ttl
        await self.client.set(self._key(user_id, token), "1", ex=ttl)

    async def is_valid(self, user_id: str, token: str) -> bool:
        return bool(await self.client.exists(self._key(user_id, token)))

    async def revoke(self, user_id: str, token: str) -> None:
        await self.client.delete(self._key(user_id, token))

    async def revoke_all(self, user_id: str) -> int:
        """Revoke all refresh tokens for a user (logout from all devices)."""
        keys = await self.client.keys(f"rt:{user_id}:*")
        return await self.client.delete(*keys) if keys else 0


token_store = TokenStore()
