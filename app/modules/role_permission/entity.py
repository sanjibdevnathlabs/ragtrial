"""
RolePermission entity model.

Represents role-to-permission mappings in the RBAC system.
"""

from sqlalchemy import BigInteger, Column, String

import constants
from database.base_model import BaseModel


class RolePermission(BaseModel):
    """
    RolePermission entity for RBAC system.

    Represents the assignment of permissions to roles.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        role_id: Foreign key to roles table (application-level)
        permission_id: Foreign key to permissions table (application-level)
        granted_by: User ID who granted this permission (nullable)
        granted_at: Timestamp when permission was granted (milliseconds)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Relationships:
        - role: Many-to-one with Role (via role_id)
        - permission: Many-to-one with Permission (via permission_id)
    """

    __tablename__ = constants.DB_TABLE_ROLE_PERMISSIONS

    # RolePermission-specific fields
    role_id = Column(
        String(36),
        nullable=False,
        index=True,
        comment="Role ID (FK to roles.id)",
    )

    permission_id = Column(
        String(36),
        nullable=False,
        index=True,
        comment="Permission ID (FK to permissions.id)",
    )

    granted_by = Column(
        String(36),
        nullable=True,
        comment="User ID who granted this permission",
    )

    granted_at = Column(
        BigInteger,
        nullable=False,
        comment="Timestamp when permission was granted (milliseconds)",
    )

    def to_dict(self) -> dict:
        """
        Convert role permission to dictionary.

        Returns:
            Dictionary with role permission data
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "role_id": self.role_id,
                "permission_id": self.permission_id,
                "granted_by": self.granted_by,
                "granted_at": self.granted_at,
            }
        )
        return base_dict

    def is_active(self) -> bool:
        """
        Check if role permission is active (not soft-deleted).

        Returns:
            True if role permission is active
        """
        return self.deleted_at is None

    def __repr__(self) -> str:
        """String representation of role permission."""
        return (
            f"<RolePermission(role_id={self.role_id}, "
            f"permission_id={self.permission_id})>"
        )

