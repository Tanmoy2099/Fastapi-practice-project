from app.core.config import settings
from app.db.redis.base import BaseRedisStore
from app.models.user import UserRole

_PERMISSION_TTL = 600  # 10 minutes


class PermissionStore(BaseRedisStore):
    """
    Cache user roles to avoid a DB round-trip on every authenticated request.

    Key pattern: perm:{user_id}
    TTL: 10 minutes (invalidated immediately on role change)

    Usage:
        from app.db.redis import permission_store
        await permission_store.set(user_id, "admin")
        role = await permission_store.get(user_id)   # "admin" or None
        await permission_store.invalidate(user_id)   # call after role change
    """

    def __init__(self) -> None:
        super().__init__(db=settings.redis_db)

    @staticmethod
    def _key(user_id: str) -> str:
        return f"perm:{user_id}"

    async def set(self, user_id: str, role: "str | UserRole") -> None:
        role_val = role.value if hasattr(role, "value") else role
        await self.client.set(self._key(user_id), role_val, ex=_PERMISSION_TTL)

    async def get(self, user_id: str) -> str | None:
        return await self.client.get(self._key(user_id))

    async def invalidate(self, user_id: str) -> None:
        await self.client.delete(self._key(user_id))


permission_store = PermissionStore()
