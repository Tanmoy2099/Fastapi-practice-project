import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

# Inject test database name before loading settings
os.environ["MONGO_DB_NAME"] = "practice_test_db"
os.environ["RATE_LIMIT_ENABLED"] = "false"  # disable rate limiter for tests

from app.main import app

@pytest.fixture(scope="session")
def client():
    """
    Returns a FastAPI TestClient. 
    Initializing TestClient automatically triggers the ASGI lifespan (connects Mongo & Redis).
    """
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture(autouse=True)
async def clear_db(client):
    """
    Clears test MongoDB and Redis before each test.
    Requires client to ensure DB lifespan is started.
    """
    from app.db.redis import cache
    from app.models.user import User
    from app.models.post import Post

    # Wait until DB is actually initialized by lifespan. 
    try:
        await User.delete_all()
        await Post.delete_all()
    except Exception:
        pass

    # Flush Redis
    try:
        await getattr(cache, 'redis').flushdb()
    except Exception:
        pass
    yield
