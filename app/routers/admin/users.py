"""
Admin Users API Router.

Provides user management operations.
Protected by RBAC permissions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from app.modules.rbac.dependencies import require_permission
from app.modules.user.service import UserService
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/admin/users", tags=["Admin - Users"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class UserResponse(BaseModel):
    """Response schema for user."""

    id: str
    email: EmailStr
    full_name: str
    status: str
    is_verified: bool
    email_verified_at: Optional[int] = None
    created_at: int
    updated_at: int
    deleted_at: Optional[int] = None


class UserUpdateRequest(BaseModel):
    """Request schema for updating user."""

    full_name: str = Field(None, min_length=1, max_length=255, description="Full name")
    status: str = Field(
        None, description="User status (active, inactive, suspended)"
    )


class UserCreateRequest(BaseModel):
    """Request schema for creating user (admin only)."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, description="User password")
    status: str = Field(
        default="active", description="User status (active, inactive, suspended)"
    )


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_user_service() -> UserService:
    """Get user service instance."""
    return UserService()


# ============================================================================
# ROUTES
# ============================================================================


@router.get(
    "",
    response_model=List[UserResponse],
    dependencies=[Depends(require_permission("user:list"))],
    summary="List all users",
)
async def list_users(
    status: Optional[str] = Query(None, description="Filter by status"),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get list of all users (optionally filtered by status).

    **Required Permission:** `user:list`
    """
    users = user_service.get_all_users()

    # Filter by status if provided
    if status:
        users = [u for u in users if u.get("status") == status]

    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("user:read"))],
    summary="Get user by ID",
)
async def get_user(
    user_id: str, user_service: UserService = Depends(get_user_service)
):
    """
    Get user details by ID.

    **Required Permission:** `user:read`
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found",
        )
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("user:create"))],
    summary="Create new user (admin)",
)
async def create_user(
    request: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user (admin operation).

    **Required Permission:** `user:create`
    """
    try:
        user = user_service.create_user_admin(
            email=request.email,
            full_name=request.full_name,
            password=request.password,
            status=request.status,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("user:update"))],
    summary="Update user",
)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Update user details.

    **Required Permission:** `user:update`
    """
    # Build update data (only include provided fields)
    update_data = {}
    if request.full_name is not None:
        update_data["full_name"] = request.full_name
    if request.status is not None:
        # Validate status
        valid_statuses = ["active", "inactive", "suspended"]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )
        update_data["status"] = request.status

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        user = user_service.update_user(user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found",
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("user:delete"))],
    summary="Delete user",
)
async def delete_user(
    user_id: str, user_service: UserService = Depends(get_user_service)
):
    """
    Soft delete a user.

    **Required Permission:** `user:delete`
    """
    deleted = user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found",
        )
    return None

