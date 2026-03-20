import logging
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.schemas.error import ErrorContent, ErrorDetail, ErrorResponse

logger = logging.getLogger("uvicorn.error")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handles our custom semantic exceptions triggered from anywhere in the app.
    """
    error_content = ErrorContent(
        code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=error_content).model_dump(exclude_none=True),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Overrides the default FastAPI 422 handler to map it to our standard schema.
    """
    details = []
    for error in exc.errors():
        details.append(
            ErrorDetail(
                loc=[str(x) for x in error.get("loc", [])],
                msg=error.get("msg", "Validation error"),
                type=error.get("type"),
            )
        )

    error_content = ErrorContent(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=details,  # type: ignore
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(error=error_content).model_dump(exclude_none=True),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Catches default Starlette/FastAPI errors (e.g., 404 URL Not Found, 405 Method Not Allowed)
    and maps them to our schema.
    """
    error_content = ErrorContent(
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=error_content).model_dump(exclude_none=True),
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all for completely unhandled errors (500).
    Logs the real error stack trace but returns a generic message to the client for security.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    error_content = ErrorContent(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred.",
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error=error_content).model_dump(exclude_none=True),
    )
