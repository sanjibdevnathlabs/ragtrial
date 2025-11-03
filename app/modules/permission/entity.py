"""
Permission entity model.

Represents permissions in the RBAC system.
"""

from sqlalchemy import Column, String, Text

import constants
from database.base_model import BaseModel


class Permission(BaseModel):
    """
    Permission entity for RBAC system.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        name: Permission name (unique, format: 'resource:action')
        resource: Resource type (e.g., 'user', 'file', 'rate_limit')
        action: Action type (e.g., 'read', 'write', 'delete', 'list')
        description: Human-readable description
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Relationships:
        - role_permissions: One-to-many with RolePermission
        - user_permissions: One-to-many with UserPermission
    """

    __tablename__ = constants.DB_TABLE_PERMISSIONS

    # Permission-specific fields
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Permission name (resource:action format)",
    )

    resource = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Resource type (user, file, rate_limit, etc.)",
    )

    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action type (read, write, delete, list, etc.)",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of permission",
    )

    def to_dict(self) -> dict:
        """
        Convert permission to dictionary.

        Returns:
            Dictionary with permission data
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "name": self.name,
                "resource": self.resource,
                "action": self.action,
                "description": self.description,
            }
        )
        return base_dict

    def is_active(self) -> bool:
        """
        Check if permission is active (not soft-deleted).

        Returns:
            True if permission is active
        """
        return self.deleted_at is None

    def __repr__(self) -> str:
        """String representation of permission."""
        return f"<Permission(id={self.id}, name={self.name})>"

