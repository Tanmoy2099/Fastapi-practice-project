import os

import mongomock_motor
import pytest
import pytest_asyncio
from fakeredis import FakeAsyncRedis
from fastapi.testclient import TestClient

# Inject test database name strictly for fallback isolation
os.environ["MONGO_DB_NAME"] = "practice_test_db"
os.environ["RATE_LIMIT_ENABLED"] = "false"  # disable rate limiter

# ── 1. Intercept Physical Drivers BEFORE the ASGI App Loads ──────────────────
import app.db.mongo as mongo
from app.db.redis.base import BaseRedisStore

# Create fake RAM instances
fake_redis = FakeAsyncRedis(decode_responses=True)
mock_mongo_client = mongomock_motor.AsyncMongoMockClient()


# Intercept Mongo connection natively
async def fake_mongo_connect(document_models):
    from beanie import init_beanie

    from app.core.config import settings

    mongo._client = mock_mongo_client
    await init_beanie(
        database=mock_mongo_client[settings.mongo_db_name], document_models=document_models
    )


mongo.connect_db = fake_mongo_connect


# Intercept ALL Redis instances globally via the Base Class
async def fake_base_redis_connect(self):
    self._client = fake_redis


BaseRedisStore.connect = fake_base_redis_connect

# Now aggressively import the application map
from app.main import app  # noqa: E402


# ── 2. Test Execution Engine ──────────────────────────────────────────────────
@pytest.fixture(scope="session")
def client():
    """
    Initializing TestClient automatically triggers the ASGI lifespan.
    Because we swapped the Python pointers above, FastAPI unknowingly boots
    into our RAM simulations identically to real production bindings.
    """
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(autouse=True)
async def clear_db(client):
    """
    Clears RAM MongoDB and FakeRedis efficiently before each E2E test.
    """
    from app.models.post import Post
    from app.models.user import User

    # Fast drop using underlying in-memory mock collections
    try:
        await User.get_motor_collection().drop()
        await Post.get_motor_collection().drop()
    except Exception:
        pass

    # Flush FakeRedis instantly
    await fake_redis.flushdb()

    yield
