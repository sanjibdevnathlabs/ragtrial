"""
Admin Permissions API Router.

Provides CRUD operations for permission management.
Protected by RBAC permissions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.modules.permission.core import PermissionService
from app.modules.rbac.dependencies import require_permission
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/admin/permissions", tags=["Admin - Permissions"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class PermissionCreateRequest(BaseModel):
    """Request schema for creating a permission."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Permission name (resource:action)"
    )
    resource: str = Field(
        ..., min_length=1, max_length=50, description="Resource type"
    )
    action: str = Field(..., min_length=1, max_length=50, description="Action type")
    description: str = Field(
        None, max_length=500, description="Permission description (optional)"
    )


class PermissionUpdateRequest(BaseModel):
    """Request schema for updating a permission."""

    name: str = Field(None, min_length=1, max_length=100, description="Permission name")
    resource: str = Field(None, min_length=1, max_length=50, description="Resource type")
    action: str = Field(None, min_length=1, max_length=50, description="Action type")
    description: str = Field(None, max_length=500, description="Permission description")


class PermissionResponse(BaseModel):
    """Response schema for permission."""

    id: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    created_at: int
    updated_at: int
    deleted_at: Optional[int] = None


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_permission_service() -> PermissionService:
    """Get permission service instance."""
    return PermissionService()


# ============================================================================
# ROUTES
# ============================================================================


@router.get(
    "",
    response_model=List[PermissionResponse],
    dependencies=[Depends(require_permission("permission:list"))],
    summary="List all permissions",
)
async def list_permissions(
    permission_service: PermissionService = Depends(get_permission_service),
):
    """
    Get list of all active permissions.

    **Required Permission:** `permission:list`
    """
    permissions = permission_service.get_all_permissions()
    return permissions


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    dependencies=[Depends(require_permission("permission:read"))],
    summary="Get permission by ID",
)
async def get_permission(
    permission_id: str,
    permission_service: PermissionService = Depends(get_permission_service),
):
    """
    Get permission details by ID.

    **Required Permission:** `permission:read`
    """
    permission = permission_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID '{permission_id}' not found",
        )
    return permission


@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("permission:create"))],
    summary="Create new permission",
)
async def create_permission(
    request: PermissionCreateRequest,
    permission_service: PermissionService = Depends(get_permission_service),
):
    """
    Create a new permission.

    **Required Permission:** `permission:create`
    """
    try:
        permission = permission_service.create_permission(
            name=request.name,
            resource=request.resource,
            action=request.action,
            description=request.description,
        )
        return permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    dependencies=[Depends(require_permission("permission:update"))],
    summary="Update permission",
)
async def update_permission(
    permission_id: str,
    request: PermissionUpdateRequest,
    permission_service: PermissionService = Depends(get_permission_service),
):
    """
    Update an existing permission.

    **Required Permission:** `permission:update`
    """
    # Build update data (only include provided fields)
    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.resource is not None:
        update_data["resource"] = request.resource
    if request.action is not None:
        update_data["action"] = request.action
    if request.description is not None:
        update_data["description"] = request.description

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        permission = permission_service.update_permission(permission_id, update_data)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID '{permission_id}' not found",
            )
        return permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("permission:delete"))],
    summary="Delete permission",
)
async def delete_permission(
    permission_id: str,
    permission_service: PermissionService = Depends(get_permission_service),
):
    """
    Soft delete a permission.

    **Required Permission:** `permission:delete`
    """
    deleted = permission_service.delete_permission(permission_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID '{permission_id}' not found",
        )
    return None

