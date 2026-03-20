from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings

# Singleton limiter — import this in routes to apply per-endpoint limits
# Usage in a route:
#   from app.middlewares.rate_limiter import limiter
#   @router.get("/")
#   @limiter.limit("10/minute")
#   async def my_route(request: Request): ...
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "detail": str(exc.detail),
            "retry_after": request.headers.get("Retry-After"),
        },
    )


def add_rate_limiter(app) -> None:
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
