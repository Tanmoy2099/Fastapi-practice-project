import redis.asyncio as aioredis
from app.core.config import settings


class BaseRedisStore:
    """
    Shared async Redis connection pool.
    All purpose-specific stores inherit from this.
    """

    def __init__(self, db: int | None = None) -> None:
        self._db = db if db is not None else settings.redis_db
        self._client: aioredis.Redis | None = None

    async def connect(self) -> None:
        self._client = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=self._db,
            password=settings.redis_password,
            decode_responses=True,
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError(
                f"{self.__class__.__name__} is not connected. Call connect() first."
            )
        return self._client
