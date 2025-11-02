"""
Admin API routers.

All admin routes are protected by RBAC permissions.
"""

from app.routers.admin import (
    permissions,
    roles,
    user_permissions,
    user_roles,
    users,
)

__all__ = [
    "roles",
    "permissions",
    "users",
    "user_roles",
    "user_permissions",
]

