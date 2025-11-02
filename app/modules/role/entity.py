"""
Role entity model.

Represents roles in the RBAC system.
"""

from sqlalchemy import Column, String, Text

import constants
from database.base_model import BaseModel


class Role(BaseModel):
    """
    Role entity for RBAC system.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        name: Role name (unique, e.g., 'admin', 'user', 'super_admin')
        description: Human-readable description of role purpose
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Relationships:
        - user_roles: One-to-many with UserRole
        - role_permissions: One-to-many with RolePermission
    """

    __tablename__ = constants.DB_TABLE_ROLES

    # Role-specific fields
    name = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Role name (admin, user, super_admin, etc.)",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of role purpose",
    )

    def to_dict(self) -> dict:
        """
        Convert role to dictionary.

        Returns:
            Dictionary with role data
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "name": self.name,
                "description": self.description,
            }
        )
        return base_dict

    def is_active(self) -> bool:
        """
        Check if role is active (not soft-deleted).

        Returns:
            True if role is active
        """
        return self.deleted_at is None

    def __repr__(self) -> str:
        """String representation of role."""
        return f"<Role(id={self.id}, name={self.name})>"

