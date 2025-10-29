"""
Common API models shared across all modules.

Contains Pydantic models used by multiple modules (cross-cutting concerns).
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """Response model for error cases (shared across all modules)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "File size exceeds maximum allowed",
                "error_code": "FILE_TOO_LARGE",
            }
        }
    )

    success: bool = Field(False, description="Upload success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
