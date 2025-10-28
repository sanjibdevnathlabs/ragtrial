"""
Health module response models.

Contains Pydantic models for health check responses.
"""

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "storage_backend": "local",
                "version": "1.0.0"
            }
        }
    )
    
    status: str = Field(..., description="Service status")
    storage_backend: str = Field(..., description="Configured storage backend")
    version: str = Field(..., description="API version")

