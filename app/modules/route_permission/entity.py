"""
RoutePermission entity model.

Represents centralized route permission configuration in the RBAC system.
"""

import json
from typing import List

from sqlalchemy import Boolean, Column, String, Text

import constants
from database.base_model import BaseModel


class RoutePermission(BaseModel):
    """
    RoutePermission entity for RBAC system.

    Represents centralized configuration of which permissions are required
    for specific API routes.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        route_name: Unique name for the route
        http_method: HTTP method (GET, POST, PUT, DELETE)
        route_path: API route path (e.g., /api/v1/admin/users)
        required_permissions: JSON array of permission names required
        description: Human-readable description
        enabled: Whether this route permission is active
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)
    """

    __tablename__ = constants.DB_TABLE_ROUTE_PERMISSIONS

    # RoutePermission-specific fields
    route_name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Unique name for the route",
    )

    http_method = Column(
        String(10),
        nullable=False,
        comment="HTTP method (GET, POST, PUT, DELETE)",
    )

    route_path = Column(
        String(500),
        nullable=False,
        comment="API route path (e.g., /api/v1/admin/users)",
    )

    required_permissions = Column(
        Text,
        nullable=False,
        comment="JSON array of permission names required for this route",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of the route permission",
    )

    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this route permission is active",
    )

    def to_dict(self) -> dict:
        """
        Convert route permission to dictionary.

        Returns:
            Dictionary with route permission data
        """
        base_dict = super().to_dict()

        # Parse required_permissions JSON array
        try:
            permissions_list = (
                json.loads(self.required_permissions)
                if self.required_permissions
                else []
            )
        except json.JSONDecodeError:
            permissions_list = []

        base_dict.update(
            {
                "route_name": self.route_name,
                "http_method": self.http_method,
                "route_path": self.route_path,
                "required_permissions": permissions_list,
                "description": self.description,
                "enabled": bool(self.enabled),
            }
        )
        return base_dict

    def get_required_permissions(self) -> List[str]:
        """
        Get list of required permission names.

        Returns:
            List of permission names
        """
        try:
            return (
                json.loads(self.required_permissions)
                if self.required_permissions
                else []
            )
        except json.JSONDecodeError:
            return []

    def set_required_permissions(self, permissions: List[str]) -> None:
        """
        Set required permissions from list.

        Args:
            permissions: List of permission names
        """
        self.required_permissions = json.dumps(permissions)

    def is_active(self) -> bool:
        """
        Check if route permission is active (not soft-deleted and enabled).

        Returns:
            True if route permission is active
        """
        return self.deleted_at is None and self.enabled

    def __repr__(self) -> str:
        """String representation of route permission."""
        return f"<RoutePermission(route_name={self.route_name}, method={self.http_method})>"

