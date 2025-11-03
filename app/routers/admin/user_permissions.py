"""
Admin User Permission Assignment API Router.

Provides operations for assigning/removing direct permissions to/from users.
Protected by RBAC permissions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.modules.rbac.dependencies import require_permission
from app.modules.user_permission.core import UserPermissionService
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/admin/user-permissions", tags=["Admin - User Permissions"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class UserPermissionAssignRequest(BaseModel):
    """Request schema for assigning permission to user."""

    user_id: str = Field(..., description="User ID")
    permission_id: str = Field(..., description="Permission ID")
    granted_by: str = Field(None, description="Admin user ID granting the permission")
    expires_at: int = Field(
        None, description="Expiration timestamp in milliseconds (optional)"
    )


class UserPermissionRemoveRequest(BaseModel):
    """Request schema for removing permission from user."""

    user_id: str = Field(..., description="User ID")
    permission_id: str = Field(..., description="Permission ID")


class UserPermissionResponse(BaseModel):
    """Response schema for user permission assignment."""

    id: str
    user_id: str
    permission_id: str
    granted_by: str = None
    granted_at: int
    expires_at: int = None
    created_at: int
    updated_at: int
    deleted_at: int = None


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_user_permission_service() -> UserPermissionService:
    """Get user permission service instance."""
    return UserPermissionService()


# ============================================================================
# ROUTES
# ============================================================================


@router.get(
    "/user/{user_id}",
    response_model=List[UserPermissionResponse],
    dependencies=[Depends(require_permission("user_permission:list"))],
    summary="Get user's direct permissions",
)
async def get_user_permissions(
    user_id: str,
    include_expired: bool = False,
    user_permission_service: UserPermissionService = Depends(
        get_user_permission_service
    ),
):
    """
    Get all direct permissions assigned to a user.

    **Required Permission:** `user_permission:list`
    """
    permissions = user_permission_service.get_user_permissions(
        user_id, include_expired=include_expired
    )
    return permissions


@router.post(
    "/assign",
    response_model=UserPermissionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("user_permission:assign"))],
    summary="Assign permission to user",
)
async def assign_permission_to_user(
    request: UserPermissionAssignRequest,
    user_permission_service: UserPermissionService = Depends(
        get_user_permission_service
    ),
):
    """
    Assign a direct permission to a user (bypassing roles).

    **Required Permission:** `user_permission:assign`
    """
    try:
        user_permission = user_permission_service.assign_permission_to_user(
            user_id=request.user_id,
            permission_id=request.permission_id,
            granted_by=request.granted_by,
            expires_at=request.expires_at,
        )
        return user_permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/remove",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("user_permission:remove"))],
    summary="Remove permission from user",
)
async def remove_permission_from_user(
    request: UserPermissionRemoveRequest,
    user_permission_service: UserPermissionService = Depends(
        get_user_permission_service
    ),
):
    """
    Remove a direct permission assignment from a user.

    **Required Permission:** `user_permission:remove`
    """
    removed = user_permission_service.remove_permission_from_user(
        user_id=request.user_id, permission_id=request.permission_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User permission assignment not found",
        )
    return None

