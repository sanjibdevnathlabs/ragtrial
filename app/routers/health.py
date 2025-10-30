"""
Health check router.

Route definitions for health check endpoints.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

import constants
from app.api.dependencies import get_health_service
from app.modules.health import HealthService
from app.modules.health.response import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "All critical components healthy",
            "content": {
                "application/json": {
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
                                "details": {
                                    "provider": "openai",
                                    "cached": "true",
                                    "cache_age_seconds": "10.5",
                                },
                            },
                            {
                                "name": "embeddings",
                                "status": "healthy",
                                "category": "dependency",
                                "details": {
                                    "provider": "openai",
                                    "cached": "true",
                                    "cache_age_seconds": "10.5",
                                },
                            },
                        ],
                    }
                }
            },
        },
        502: {
            "description": "One or more critical components unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "version": "1.0.0",
                        "components": [
                            {
                                "name": "database",
                                "status": "unhealthy",
                                "category": "critical",
                                "details": {
                                    "type": "mysql",
                                    "error": "Connection refused",
                                },
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
            },
        },
    },
)
async def health_check(service: HealthService = Depends(get_health_service)):
    """
    Health check endpoint with component-level status.

    Performs fast health checks on critical components (database, vectorstore)
    and cached checks on external dependencies (LLM, Embeddings APIs).

    **Critical Components (uncached):**
    - Database: Connection pool ping (~1-5ms)
    - Vectorstore: Heartbeat/API check (~10-50ms)

    **Dependencies (60-second cache):**
    - LLM API: Availability check (cached to reduce costs)
    - Embeddings API: Availability check (cached to reduce costs)

    **HTTP Status Codes:**
    - 200 OK: All critical components (database, vectorstore) are healthy
    - 502 Bad Gateway: Any critical component is unhealthy

    **Response Format:**
    - `status`: Overall status ("healthy" or "unhealthy")
    - `version`: API version
    - `components`: Array of component statuses with details

    Each component includes:
    - `name`: Component identifier
    - `status`: "healthy" or "unhealthy"
    - `category`: "critical" (required) or "dependency" (optional)
    - `details`: Type/provider info, error messages, cache status

    Returns:
        - 200 OK: System is healthy
        - 502 Bad Gateway: System is unhealthy (critical component failure)
    """
    health_response = service.get_health_status()

    # Return 502 if any critical component is unhealthy
    if health_response.status == constants.HEALTH_STATUS_UNHEALTHY:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=health_response.model_dump(),
        )

    # Return 200 for healthy
    return health_response
