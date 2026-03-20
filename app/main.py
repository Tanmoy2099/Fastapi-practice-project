from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.routes.routes import routes
from app.core.config import settings
from app.db.mongo import connect_db, close_db
from app.db.redis import cache, token_store, permission_store
from app.models.post import Post
from app.models.user import User
from app.middlewares.cors import add_cors
from app.middlewares.rate_limiter import add_rate_limiter
from app.middlewares.mongo_sanitizer import add_mongo_sanitizer
from app.middlewares.security_headers import add_security_headers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────
    await connect_db(document_models=[User, Post])
    await cache.connect()
    await token_store.connect()
    await permission_store.connect()
    yield
    # ── Shutdown ──────────────────────────────────
    await close_db()
    await cache.close()
    await token_store.close()
    await permission_store.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# ── Middleware stack (Starlette applies bottom-up) ────────────────────────────
add_security_headers(app)
add_mongo_sanitizer(app)
add_rate_limiter(app)
add_cors(app)

# ── Routes ────────────────────────────────────────────────────────────────────
for route in routes:
    app.include_router(**route)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
