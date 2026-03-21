import json
import re
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Patterns that indicate a NoSQL injection attempt
_DANGEROUS_KEYS = re.compile(r"^\$")
_DANGEROUS_VALUES = re.compile(
    r"\$where|\$regex|\$ne|\$gt|\$lt|\$gte|\$lte|\$in|\$nin|\$or|\$and|\$not|\$nor|\$exists|\$type|\$expr",
    re.IGNORECASE,
)


def _sanitize(data: Any, depth: int = 0) -> Any:
    """
    Recursively strip MongoDB operator keys/values from parsed JSON.
    Raises ValueError if an injection pattern is detected.
    """
    if depth > 20:
        raise ValueError("Payload nesting too deep")

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if _DANGEROUS_KEYS.match(str(key)):
                raise ValueError(f"Forbidden key: '{key}'")
            sanitized[key] = _sanitize(value, depth + 1)
        return sanitized

    if isinstance(data, list):
        return [_sanitize(item, depth + 1) for item in data]

    if isinstance(data, str) and _DANGEROUS_VALUES.search(data):
        raise ValueError(f"Forbidden value pattern detected: '{data}'")

    return data


class MongoSanitizerMiddleware(BaseHTTPMiddleware):
    """
    Inspect JSON request bodies and reject any that contain MongoDB
    operator keys (e.g. $where, $gt) or dangerous value patterns.
    Only applied to methods that carry a body.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    raw = await request.body()
                    if raw:
                        body = json.loads(raw)
                        _sanitize(body)
                except ValueError as exc:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Invalid input", "detail": str(exc)},
                    )
                except json.JSONDecodeError:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Malformed JSON body"},
                    )

        return await call_next(request)


def add_mongo_sanitizer(app) -> None:
    app.add_middleware(MongoSanitizerMiddleware)
