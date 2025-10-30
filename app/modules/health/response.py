"""
Health module response models.

Contains Pydantic models for health check responses.
"""

from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ComponentHealth(BaseModel):
    """Health status for individual component."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "database",
                "status": "healthy",
                "category": "critical",
                "details": {"type": "sqlite"},
            }
        }
    )

    name: str = Field(..., description="Component name")
    status: str = Field(..., description="healthy or unhealthy")
    category: str = Field(..., description="critical or dependency")
    details: Dict[str, str] = Field(
        default_factory=dict, description="Additional details"
    )


class HealthResponse(BaseModel):
    """Response model for health check."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "components": [
                    {
                        "name": "database",
                        "status": "healthy",
                        "category": "critical",
                        "details": {"type": "sqlite"},
                    },
                    {
                        "name": "vectorstore",
                        "status": "healthy",
                        "category": "critical",
                        "details": {"provider": "chroma"},
                    },
                    {
                        "name": "llm",
                        "status": "healthy",
                        "category": "dependency",
                        "details": {"provider": "openai", "cached": "true"},
                    },
                    {
                        "name": "embeddings",
                        "status": "healthy",
                        "category": "dependency",
                        "details": {"provider": "openai", "cached": "true"},
                    },
                ],
            }
        }
    )

    status: str = Field(..., description="Overall service status (healthy/unhealthy)")
    version: str = Field(..., description="API version")
    components: List[ComponentHealth] = Field(
        ..., description="Individual component health statuses"
    )
