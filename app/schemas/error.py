from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: Optional[str] = None


class ErrorContent(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None


class ErrorResponse(BaseModel):
    """
    Standardized error response wrapper.
    Matches the schema:
    {
      "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": []
      }
    }
    """

    error: ErrorContent

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "The requested resource was not found.",
                    "details": None,
                }
            }
        }
    )
