"""
UserRole entity model.

Represents user-to-role mappings in the RBAC system.
"""

from sqlalchemy import BigInteger, Column, String

import constants
from database.base_model import BaseModel


class UserRole(BaseModel):
    """
    UserRole entity for RBAC system.

    Represents the assignment of roles to users with optional expiration.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table (application-level)
        role_id: Foreign key to roles table (application-level)
        granted_by: User ID who granted this role (nullable)
        granted_at: Timestamp when role was granted (milliseconds)
        expires_at: Timestamp when role expires (nullable, milliseconds)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Relationships:
        - user: Many-to-one with User (via user_id)
        - role: Many-to-one with Role (via role_id)
    """

    __tablename__ = constants.DB_TABLE_USER_ROLES

    # UserRole-specific fields
    user_id = Column(
        String(36),
        nullable=False,
        index=True,
        comment="User ID (FK to users.id)",
    )

    role_id = Column(
        String(36),
        nullable=False,
        index=True,
        comment="Role ID (FK to roles.id)",
    )

    granted_by = Column(
        String(36),
        nullable=True,
        comment="User ID who granted this role",
    )

    granted_at = Column(
        BigInteger,
        nullable=False,
        comment="Timestamp when role was granted (milliseconds)",
    )

    expires_at = Column(
        BigInteger,
        nullable=True,
        comment="Timestamp when role expires (nullable, milliseconds)",
    )

    def to_dict(self) -> dict:
        """
        Convert user role to dictionary.

        Returns:
            Dictionary with user role data
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "user_id": self.user_id,
                "role_id": self.role_id,
                "granted_by": self.granted_by,
                "granted_at": self.granted_at,
                "expires_at": self.expires_at,
            }
        )
        return base_dict

    def is_active(self) -> bool:
        """
        Check if user role is active (not soft-deleted).

        Returns:
            True if user role is active
        """
        return self.deleted_at is None

    def is_expired(self, current_time_ms: int) -> bool:
        """
        Check if role assignment has expired.

        Args:
            current_time_ms: Current timestamp in milliseconds

        Returns:
            True if expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return current_time_ms > self.expires_at

    def __repr__(self) -> str:
        """String representation of user role."""
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"

