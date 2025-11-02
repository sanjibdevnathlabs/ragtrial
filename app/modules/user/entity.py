"""
User entity model.

Represents user account information for authentication and profile management.
"""

import uuid
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, String

import constants
from database.base_model import BaseModel


class User(BaseModel):
    """
    User entity for authentication and profile management.

    Fields:
        id: UUID primary key
        email: User's email address (unique, used for login)
        password_hash: Hashed password (nullable for OAuth-only users)
        full_name: User's full name (e.g., "John Doe")
        avatar_url: URL to user's avatar image
        is_verified: Whether email has been verified
        email_verified_at: Timestamp of email verification (milliseconds)
        status: Account status (active, inactive, suspended)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Indexes:
        - unique_email: Unique constraint on email
        - idx_users_status: For querying users by status
        - idx_users_is_verified: For querying verified/unverified users
        - idx_users_deleted_at: For filtering active vs deleted users

    Relationships:
        - oauth_providers: One-to-many with OAuthProvider
        - refresh_tokens: One-to-many with RefreshToken
        - password_reset_tokens: One-to-many with PasswordResetToken
        - files: One-to-many with File
    """

    __tablename__ = constants.DB_TABLE_USERS

    # Override table name from base model
    __table_args__ = {"extend_existing": True}

    # User-specific fields
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False, index=True)
    email_verified_at = Column(BigInteger, nullable=True)
    status = Column(
        String(50), nullable=False, default=constants.USER_STATUS_ACTIVE, index=True
    )

    @staticmethod
    def generate_id() -> str:
        """
        Generate a new UUID for user ID.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    def mark_as_verified(self) -> None:
        """
        Mark user's email as verified.

        Updates is_verified flag and sets email_verified_at timestamp.
        """
        self.is_verified = True
        self.email_verified_at = self._get_current_timestamp()
        self.update_timestamp()

    def is_active(self) -> bool:
        """
        Check if user account is active.

        Returns:
            True if status is 'active', False otherwise
        """
        return self.status == constants.USER_STATUS_ACTIVE

    def is_suspended(self) -> bool:
        """
        Check if user account is suspended.

        Returns:
            True if status is 'suspended', False otherwise
        """
        return self.status == constants.USER_STATUS_SUSPENDED

    def suspend(self) -> None:
        """
        Suspend user account.

        Changes status to 'suspended'.
        """
        self.status = constants.USER_STATUS_SUSPENDED
        self.update_timestamp()

    def activate(self) -> None:
        """
        Activate user account.

        Changes status to 'active'.
        """
        self.status = constants.USER_STATUS_ACTIVE
        self.update_timestamp()

    def deactivate(self) -> None:
        """
        Deactivate user account.

        Changes status to 'inactive'.
        """
        self.status = constants.USER_STATUS_INACTIVE
        self.update_timestamp()

    def has_password(self) -> bool:
        """
        Check if user has a password set.

        Returns:
            True if password_hash exists, False for OAuth-only users
        """
        return self.password_hash is not None

    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """
        Convert to dictionary with additional computed fields.

        Args:
            exclude: Fields to exclude (password_hash always excluded)

        Returns:
            Dictionary representation
        """
        # Always exclude password_hash for security
        if exclude is None:
            exclude = []
        exclude.append("password_hash")

        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["is_active"] = self.is_active()
        data["is_suspended"] = self.is_suspended()
        data["is_deleted"] = self.is_deleted()
        data["has_password"] = self.has_password()

        return data

    def __repr__(self) -> str:
        """String representation."""
        status_str = f" ({self.status.upper()})"
        verified_str = " ✓" if self.is_verified else ""
        deleted = " (DELETED)" if self.is_deleted() else ""
        return (
            f"<User(id={self.id!r}, email={self.email!r})"
            f"{status_str}{verified_str}{deleted}>"
        )

