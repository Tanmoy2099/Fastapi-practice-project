from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.routes.routes import routes
from app.core.config import settings
from app.db.mongo import connect_db, close_db
from app.db.redis import cache
from app.models.post import Post

# Middlewares
from app.middlewares.cors import add_cors
from app.middlewares.rate_limiter import add_rate_limiter
from app.middlewares.mongo_sanitizer import add_mongo_sanitizer
from app.middlewares.security_headers import add_security_headers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db(document_models=[Post])
    await cache.connect()
    yield
    await close_db()
    await cache.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# ── Middleware stack (applied bottom-up by Starlette) ─────────────────────────
add_security_headers(app)   # outermost — wraps every response
add_mongo_sanitizer(app)    # sanitize request bodies before they reach routes
add_rate_limiter(app)       # rate limit after sanitization
add_cors(app)               # innermost — CORS must be closest to the app

# ── Routes ────────────────────────────────────────────────────────────────────
for route in routes:
    app.include_router(**route)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
