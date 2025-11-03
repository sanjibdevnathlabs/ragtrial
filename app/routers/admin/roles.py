"""
Admin Roles API Router.

Provides CRUD operations for role management.
Protected by RBAC permissions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.modules.rbac.dependencies import require_permission
from app.modules.role.core import RoleService
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/admin/roles", tags=["Admin - Roles"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class RoleCreateRequest(BaseModel):
    """Request schema for creating a role."""

    name: str = Field(..., min_length=1, max_length=50, description="Role name")
    description: str = Field(
        None, max_length=500, description="Role description (optional)"
    )


class RoleUpdateRequest(BaseModel):
    """Request schema for updating a role."""

    name: str = Field(None, min_length=1, max_length=50, description="Role name")
    description: str = Field(None, max_length=500, description="Role description")


class RoleResponse(BaseModel):
    """Response schema for role."""

    id: str
    name: str
    description: Optional[str] = None
    created_at: int
    updated_at: int
    deleted_at: Optional[int] = None


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_role_service() -> RoleService:
    """Get role service instance."""
    return RoleService()


# ============================================================================
# ROUTES
# ============================================================================


@router.get(
    "",
    response_model=List[RoleResponse],
    dependencies=[Depends(require_permission("role:list"))],
    summary="List all roles",
)
async def list_roles(role_service: RoleService = Depends(get_role_service)):
    """
    Get list of all active roles.

    **Required Permission:** `role:list`
    """
    roles = role_service.get_all_roles()
    return roles


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("role:read"))],
    summary="Get role by ID",
)
async def get_role(
    role_id: str, role_service: RoleService = Depends(get_role_service)
):
    """
    Get role details by ID.

    **Required Permission:** `role:read`
    """
    role = role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID '{role_id}' not found",
        )
    return role


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("role:create"))],
    summary="Create new role",
)
async def create_role(
    request: RoleCreateRequest, role_service: RoleService = Depends(get_role_service)
):
    """
    Create a new role.

    **Required Permission:** `role:create`
    """
    try:
        role = role_service.create_role(
            name=request.name, description=request.description
        )
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("role:update"))],
    summary="Update role",
)
async def update_role(
    role_id: str,
    request: RoleUpdateRequest,
    role_service: RoleService = Depends(get_role_service),
):
    """
    Update an existing role.

    **Required Permission:** `role:update`
    """
    # Build update data (only include provided fields)
    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.description is not None:
        update_data["description"] = request.description

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        role = role_service.update_role(role_id, update_data)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID '{role_id}' not found",
            )
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("role:delete"))],
    summary="Delete role",
)
async def delete_role(
    role_id: str, role_service: RoleService = Depends(get_role_service)
):
    """
    Soft delete a role.

    **Required Permission:** `role:delete`
    """
    deleted = role_service.delete_role(role_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID '{role_id}' not found",
        )
    return None

