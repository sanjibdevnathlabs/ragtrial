"""
UserPermission entity model.

Represents direct user-to-permission mappings in the RBAC system.
"""

from sqlalchemy import BigInteger, Column, String

import constants
from database.base_model import BaseModel


class UserPermission(BaseModel):
    """
    UserPermission entity for RBAC system.

    Represents direct assignment of permissions to users (bypassing roles)
    with optional expiration.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table (application-level)
        permission_id: Foreign key to permissions table (application-level)
        granted_by: User ID who granted this permission (nullable)
        granted_at: Timestamp when permission was granted (milliseconds)
        expires_at: Timestamp when permission expires (nullable, milliseconds)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Relationships:
        - user: Many-to-one with User (via user_id)
        - permission: Many-to-one with Permission (via permission_id)
    """

    __tablename__ = constants.DB_TABLE_USER_PERMISSIONS

    # UserPermission-specific fields
    user_id = Column(
        String(36),
        nullable=False,
        index=True,
        comment="User ID (FK to users.id)",
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

    expires_at = Column(
        BigInteger,
        nullable=True,
        comment="Timestamp when permission expires (nullable, milliseconds)",
    )

    def to_dict(self) -> dict:
        """
        Convert user permission to dictionary.

        Returns:
            Dictionary with user permission data
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "user_id": self.user_id,
                "permission_id": self.permission_id,
                "granted_by": self.granted_by,
                "granted_at": self.granted_at,
                "expires_at": self.expires_at,
            }
        )
        return base_dict

    def is_active(self) -> bool:
        """
        Check if user permission is active (not soft-deleted).

        Returns:
            True if user permission is active
        """
        return self.deleted_at is None

    def is_expired(self, current_time_ms: int) -> bool:
        """
        Check if permission assignment has expired.

        Args:
            current_time_ms: Current timestamp in milliseconds

        Returns:
            True if expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return current_time_ms > self.expires_at

    def __repr__(self) -> str:
        """String representation of user permission."""
        return (
            f"<UserPermission(user_id={self.user_id}, "
            f"permission_id={self.permission_id})>"
        )

