"""
RBAC FastAPI dependencies for route protection.

Provides decorators and dependencies for protecting routes with permissions.
"""

from typing import Callable, List

from fastapi import Depends, HTTPException, status

import trace.codes as codes
from app.modules.auth.dependencies import get_current_user
from app.modules.rbac.core import PermissionService
from logger import get_logger

logger = get_logger(__name__)

# Singleton instance
_permission_service = None


def get_permission_service() -> PermissionService:
    """
    Get or create permission service singleton.

    Returns:
        PermissionService instance
    """
    global _permission_service
    if _permission_service is None:
        _permission_service = PermissionService()
    return _permission_service


def require_permission(permission_name: str) -> Callable:
    """
    FastAPI dependency to require a specific permission.

    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_permission("user:read"))])
        async def list_users():
            ...

    Args:
        permission_name: Permission name required (e.g., "user:read")

    Returns:
        FastAPI dependency function
    """

    async def check_permission(
        current_user: dict = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service),
    ) -> dict:
        """Check if current user has required permission."""
        user_id = current_user.get("id")

        if not permission_service.user_has_permission(user_id, permission_name):
            logger.warning(
                codes.RBAC_PERMISSION_DENIED,
                user_id=user_id,
                permission=permission_name,
                route="access_denied",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required",
            )

        logger.debug(
            codes.RBAC_PERMISSION_GRANTED,
            user_id=user_id,
            permission=permission_name,
        )

        return current_user

    return check_permission


def require_any_permission(*permission_names: str) -> Callable:
    """
    FastAPI dependency to require ANY of the given permissions (OR logic).

    Usage:
        @router.get(
            "/admin/users",
            dependencies=[Depends(require_any_permission("user:read", "user:admin"))]
        )
        async def list_users():
            ...

    Args:
        *permission_names: Variable number of permission names

    Returns:
        FastAPI dependency function
    """

    async def check_any_permission(
        current_user: dict = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service),
    ) -> dict:
        """Check if current user has any of the required permissions."""
        user_id = current_user.get("id")

        if not permission_service.user_has_any_permission(
            user_id, list(permission_names)
        ):
            logger.warning(
                codes.RBAC_PERMISSION_DENIED,
                user_id=user_id,
                permissions=permission_names,
                route="access_denied",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(permission_names)}",
            )

        logger.debug(
            codes.RBAC_ANY_PERMISSION_GRANTED,
            user_id=user_id,
            permissions=permission_names,
        )

        return current_user

    return check_any_permission


def require_all_permissions(*permission_names: str) -> Callable:
    """
    FastAPI dependency to require ALL of the given permissions (AND logic).

    Usage:
        @router.delete(
            "/admin/users/{user_id}",
            dependencies=[Depends(require_all_permissions("user:delete", "admin:access"))]
        )
        async def delete_user(user_id: str):
            ...

    Args:
        *permission_names: Variable number of permission names

    Returns:
        FastAPI dependency function
    """

    async def check_all_permissions(
        current_user: dict = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service),
    ) -> dict:
        """Check if current user has all of the required permissions."""
        user_id = current_user.get("id")

        if not permission_service.user_has_all_permissions(
            user_id, list(permission_names)
        ):
            logger.warning(
                codes.RBAC_PERMISSION_DENIED,
                user_id=user_id,
                permissions=permission_names,
                route="access_denied",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All these permissions required: {', '.join(permission_names)}",
            )

        logger.debug(
            codes.RBAC_ALL_PERMISSIONS_GRANTED,
            user_id=user_id,
            permissions=permission_names,
        )

        return current_user

    return check_all_permissions


async def get_current_user_permissions(
    current_user: dict = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
) -> List[str]:
    """
    FastAPI dependency to inject user's permissions into route.

    Usage:
        @router.get("/me/permissions")
        async def get_my_permissions(
            permissions: List[str] = Depends(get_current_user_permissions)
        ):
            return {"permissions": permissions}

    Args:
        current_user: Current authenticated user (from get_current_user)
        permission_service: Permission service instance

    Returns:
        List of user's permission names
    """
    user_id = current_user.get("id")
    permissions = permission_service.get_all_user_permissions(user_id)

    logger.debug(
        codes.RBAC_USER_PERMISSIONS_INJECTED,
        user_id=user_id,
        count=len(permissions),
    )

    return permissions


async def get_current_user_roles(
    current_user: dict = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
) -> List[dict]:
    """
    FastAPI dependency to inject user's roles into route.

    Usage:
        @router.get("/me/roles")
        async def get_my_roles(roles: List[dict] = Depends(get_current_user_roles)):
            return {"roles": roles}

    Args:
        current_user: Current authenticated user
        permission_service: Permission service instance

    Returns:
        List of user's role details
    """
    user_id = current_user.get("id")
    roles = permission_service.get_user_effective_roles(user_id)

    logger.debug(
        codes.RBAC_USER_ROLES_INJECTED,
        user_id=user_id,
        count=len(roles),
    )

    return roles

