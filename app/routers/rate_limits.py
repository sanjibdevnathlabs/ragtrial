"""
Rate limit configuration management router.

Admin endpoints for managing runtime rate limit configurations.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.modules.ratelimit.config_service import RateLimitConfigService
from app.modules.rbac.dependencies import require_permission

router = APIRouter(prefix="/api/v1/admin/rate-limits", tags=["Admin - Rate Limits"])


# ============================================================================
# Request/Response Models
# ============================================================================


class RateLimitConfigResponse(BaseModel):
    """Rate limit config response."""

    id: str
    route_name: str
    requests: int
    window_seconds: int
    enabled: bool
    description: Optional[str] = None
    created_at: int
    updated_at: int


class CreateRateLimitConfigRequest(BaseModel):
    """Create rate limit config request."""

    route_name: str = Field(..., description="Route name or 'global' for default")
    requests: int = Field(..., gt=0, description="Number of requests allowed")
    window_seconds: int = Field(..., gt=0, description="Time window in seconds")
    enabled: bool = Field(True, description="Enable this limit")
    description: Optional[str] = Field(None, description="Human-readable description")


class UpdateRateLimitConfigRequest(BaseModel):
    """Update rate limit config request."""

    requests: Optional[int] = Field(None, gt=0, description="New requests limit")
    window_seconds: Optional[int] = Field(None, gt=0, description="New window")
    enabled: Optional[bool] = Field(None, description="Enable/disable")
    description: Optional[str] = Field(None, description="New description")


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str


# ============================================================================
# Routes
# ============================================================================


@router.get(
    "",
    response_model=List[RateLimitConfigResponse],
    dependencies=[Depends(require_permission("rate_limit:list"))],
    summary="List all rate limit configs",
)
async def list_rate_limit_configs():
    """
    List all rate limit configurations.

    **Required Permission:** `rate_limit:list`
    """
    service = RateLimitConfigService()
    configs = service.get_all_configs()
    return configs


@router.get(
    "/{route_name}",
    response_model=RateLimitConfigResponse,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_permission("rate_limit:read"))],
    summary="Get rate limit config for route",
)
async def get_rate_limit_config(route_name: str):
    """
    Get rate limit configuration for specific route.

    Falls back to global default if route-specific config not found.

    **Required Permission:** `rate_limit:read`
    """
    service = RateLimitConfigService()
    config = service.get_route_config(route_name)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rate limit config for '{route_name}' not found",
        )

    return config


@router.post(
    "",
    response_model=RateLimitConfigResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
    dependencies=[Depends(require_permission("rate_limit:create"))],
    summary="Create rate limit config",
)
async def create_rate_limit_config(data: CreateRateLimitConfigRequest):
    """
    Create new rate limit configuration.

    Use route_name='global' for global default.

    **Required Permission:** `rate_limit:create`
    """
    service = RateLimitConfigService()

    try:
        config = service.create_config(
            route_name=data.route_name,
            requests=data.requests,
            window_seconds=data.window_seconds,
            enabled=data.enabled,
            description=data.description,
        )
        return config
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{route_name}",
    response_model=RateLimitConfigResponse,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_permission("rate_limit:update"))],
    summary="Update rate limit config",
)
async def update_rate_limit_config(
    route_name: str,
    data: UpdateRateLimitConfigRequest,
):
    """
    Update rate limit configuration.

    Only provided fields will be updated.

    **Required Permission:** `rate_limit:update`
    """
    service = RateLimitConfigService()

    config = service.update_config(
        route_name=route_name,
        requests=data.requests,
        window_seconds=data.window_seconds,
        enabled=data.enabled,
        description=data.description,
    )

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rate limit config for '{route_name}' not found",
        )

    return config


@router.delete(
    "/{route_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_permission("rate_limit:delete"))],
    summary="Delete rate limit config",
)
async def delete_rate_limit_config(route_name: str):
    """
    Delete rate limit configuration.

    After deletion, route will fall back to global default.

    **Required Permission:** `rate_limit:delete`
    """
    service = RateLimitConfigService()

    if not service.delete_config(route_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rate limit config for '{route_name}' not found",
        )


@router.post(
    "/{route_name}/enable",
    response_model=dict,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_permission("rate_limit:update"))],
    summary="Enable rate limit for route",
)
async def enable_rate_limit(route_name: str):
    """
    Enable rate limiting for specific route.

    **Required Permission:** `rate_limit:update`
    """
    service = RateLimitConfigService()

    if not service.enable_route(route_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rate limit config for '{route_name}' not found",
        )

    return {"message": f"Rate limit enabled for '{route_name}'"}


@router.post(
    "/{route_name}/disable",
    response_model=dict,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_permission("rate_limit:update"))],
    summary="Disable rate limit for route",
)
async def disable_rate_limit(route_name: str):
    """
    Disable rate limiting for specific route.

    **Required Permission:** `rate_limit:update`
    """
    service = RateLimitConfigService()

    if not service.disable_route(route_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rate limit config for '{route_name}' not found",
        )

    return {"message": f"Rate limit disabled for '{route_name}'"}

