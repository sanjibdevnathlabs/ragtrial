"""
Admin User Role Assignment API Router.

Provides operations for assigning/removing roles to/from users.
Protected by RBAC permissions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.modules.rbac.dependencies import require_permission
from app.modules.user_role.core import UserRoleService
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/admin/user-roles", tags=["Admin - User Roles"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class UserRoleAssignRequest(BaseModel):
    """Request schema for assigning role to user."""

    user_id: str = Field(..., description="User ID")
    role_id: str = Field(..., description="Role ID")
    granted_by: str = Field(None, description="Admin user ID granting the role")
    expires_at: int = Field(
        None, description="Expiration timestamp in milliseconds (optional)"
    )


class UserRoleRemoveRequest(BaseModel):
    """Request schema for removing role from user."""

    user_id: str = Field(..., description="User ID")
    role_id: str = Field(..., description="Role ID")


class UserRoleResponse(BaseModel):
    """Response schema for user role assignment."""

    id: str
    user_id: str
    role_id: str
    granted_by: str = None
    granted_at: int
    expires_at: int = None
    created_at: int
    updated_at: int
    deleted_at: int = None


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_user_role_service() -> UserRoleService:
    """Get user role service instance."""
    return UserRoleService()


# ============================================================================
# ROUTES
# ============================================================================


@router.get(
    "/user/{user_id}",
    response_model=List[UserRoleResponse],
    dependencies=[Depends(require_permission("user_role:list"))],
    summary="Get user's roles",
)
async def get_user_roles(
    user_id: str,
    include_expired: bool = False,
    user_role_service: UserRoleService = Depends(get_user_role_service),
):
    """
    Get all roles assigned to a user.

    **Required Permission:** `user_role:list`
    """
    roles = user_role_service.get_user_roles(user_id, include_expired=include_expired)
    return roles


@router.post(
    "/assign",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("user_role:assign"))],
    summary="Assign role to user",
)
async def assign_role_to_user(
    request: UserRoleAssignRequest,
    user_role_service: UserRoleService = Depends(get_user_role_service),
):
    """
    Assign a role to a user.

    **Required Permission:** `user_role:assign`
    """
    try:
        user_role = user_role_service.assign_role_to_user(
            user_id=request.user_id,
            role_id=request.role_id,
            granted_by=request.granted_by,
            expires_at=request.expires_at,
        )
        return user_role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/remove",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("user_role:remove"))],
    summary="Remove role from user",
)
async def remove_role_from_user(
    request: UserRoleRemoveRequest,
    user_role_service: UserRoleService = Depends(get_user_role_service),
):
    """
    Remove a role assignment from a user.

    **Required Permission:** `user_role:remove`
    """
    removed = user_role_service.remove_role_from_user(
        user_id=request.user_id, role_id=request.role_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User role assignment not found",
        )
    return None


@router.get(
    "/role/{role_id}",
    response_model=List[UserRoleResponse],
    dependencies=[Depends(require_permission("user_role:list"))],
    summary="Get users with specific role",
)
async def get_role_users(
    role_id: str,
    user_role_service: UserRoleService = Depends(get_user_role_service),
):
    """
    Get all users assigned to a specific role.

    **Required Permission:** `user_role:list`
    """
    users = user_role_service.get_role_users(role_id)
    return users

