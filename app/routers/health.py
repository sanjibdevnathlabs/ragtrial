"""
Health check router.

Route definitions for health check endpoints.
"""

from fastapi import APIRouter, Depends

from app.api.models import HealthResponse
from app.modules.health import HealthService
from app.api.dependencies import get_health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(service: HealthService = Depends(get_health_service)):
    """
    Health check endpoint.
    
    Returns service status and configuration info.
    
    Returns:
        HealthResponse: Service health status
    """
    return service.get_health_status()

