"""
Token entity models.

Represents refresh tokens and password reset tokens for authentication.
"""

import json
import uuid
from typing import Optional

from sqlalchemy import BigInteger, Column, String, Text

import constants
from database.base_model import BaseModel


class RefreshToken(BaseModel):
    """
    Refresh token entity for JWT token refresh.

    Stores refresh tokens used to obtain new access tokens without re-authentication.

    Fields:
        id: UUID primary key
        user_id: Foreign key to users table (application-level)
        token_hash: SHA-256 hash of the refresh token (unique)
        metadata: JSON string containing client metadata (user_agent, ip_address)
        expires_at: Timestamp when token expires (milliseconds)
        revoked_at: Timestamp when token was revoked (NULL = active)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Indexes:
        - unique_token_hash: Ensures refresh token hash uniqueness
        - idx_refresh_tokens_user_id: For fast lookup of user's refresh tokens
        - idx_refresh_tokens_expires_at: For cleaning up expired tokens
        - idx_refresh_tokens_revoked_at: For filtering active vs revoked tokens
        - idx_refresh_tokens_deleted_at: For filtering active vs deleted records

    Relationships:
        - user: Many-to-one with User (via user_id)
    """

    __tablename__ = constants.DB_TABLE_REFRESH_TOKENS

    # Override table name from base model
    __table_args__ = {"extend_existing": True}

    # Refresh token-specific fields
    user_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    client_metadata = Column("metadata", Text, nullable=True)
    expires_at = Column(BigInteger, nullable=False, index=True)
    revoked_at = Column(BigInteger, nullable=True, index=True)

    @staticmethod
    def generate_id() -> str:
        """
        Generate a new UUID for refresh token ID.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    def set_metadata(self, data: dict) -> None:
        """
        Set metadata as JSON string.

        Args:
            data: Dictionary containing client metadata (user_agent, ip_address)
        """
        self.client_metadata = json.dumps(data)
        self.update_timestamp()

    def get_metadata(self) -> Optional[dict]:
        """
        Get metadata as dictionary.

        Returns:
            Dictionary containing client metadata, or None if not set
        """
        if self.client_metadata:
            try:
                return json.loads(self.metadata)
            except json.JSONDecodeError:
                return None
        return None

    def is_expired(self) -> bool:
        """
        Check if token has expired.

        Returns:
            True if current time > expires_at, False otherwise
        """
        current_time = self._get_current_timestamp()
        return current_time > self.expires_at

    def is_revoked(self) -> bool:
        """
        Check if token has been revoked.

        Returns:
            True if revoked_at is set, False otherwise
        """
        return self.revoked_at is not None

    def is_valid(self) -> bool:
        """
        Check if token is valid (not expired, not revoked, not deleted).

        Returns:
            True if token is valid, False otherwise
        """
        return (
            not self.is_expired()
            and not self.is_revoked()
            and not self.is_deleted()
        )

    def revoke(self) -> None:
        """
        Revoke the refresh token.

        Sets revoked_at timestamp to current time.
        """
        self.revoked_at = self._get_current_timestamp()
        self.update_timestamp()

    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """
        Convert to dictionary with additional computed fields.

        Args:
            exclude: Fields to exclude (token_hash always excluded)

        Returns:
            Dictionary representation
        """
        # Always exclude token_hash for security
        if exclude is None:
            exclude = []
        exclude.append("token_hash")

        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["is_expired"] = self.is_expired()
        data["is_revoked"] = self.is_revoked()
        data["is_valid"] = self.is_valid()
        data["is_deleted"] = self.is_deleted()

        return data

    def __repr__(self) -> str:
        """String representation."""
        status = "REVOKED" if self.is_revoked() else "EXPIRED" if self.is_expired() else "VALID"
        deleted = " (DELETED)" if self.is_deleted() else ""
        return (
            f"<RefreshToken(id={self.id!r}, user_id={self.user_id!r}, "
            f"status={status}){deleted}>"
        )


class PasswordResetToken(BaseModel):
    """
    Password reset token entity for password recovery.

    Stores tokens used for password reset requests. Only one active token
    per user should exist at a time.

    Fields:
        id: UUID primary key
        user_id: Foreign key to users table (application-level)
        token_hash: SHA-256 hash of the reset token (unique)
        metadata: JSON string containing client metadata (user_agent, ip_address)
        expires_at: Timestamp when token expires (milliseconds)
        used_at: Timestamp when token was used (NULL = active)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Indexes:
        - unique_reset_token_hash: Ensures reset token hash uniqueness
        - idx_password_reset_tokens_user_id: For fast lookup of user's reset tokens
        - idx_password_reset_tokens_expires_at: For cleaning up expired tokens
        - idx_password_reset_tokens_used_at: For filtering active vs used tokens
        - idx_password_reset_tokens_deleted_at: For filtering active vs deleted records

    Relationships:
        - user: Many-to-one with User (via user_id)
    """

    __tablename__ = constants.DB_TABLE_PASSWORD_RESET_TOKENS

    # Override table name from base model
    __table_args__ = {"extend_existing": True}

    # Password reset token-specific fields
    user_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    client_metadata = Column("metadata", Text, nullable=True)
    expires_at = Column(BigInteger, nullable=False, index=True)
    used_at = Column(BigInteger, nullable=True, index=True)

    @staticmethod
    def generate_id() -> str:
        """
        Generate a new UUID for password reset token ID.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    def set_metadata(self, data: dict) -> None:
        """
        Set metadata as JSON string.

        Args:
            data: Dictionary containing client metadata (user_agent, ip_address)
        """
        self.client_metadata = json.dumps(data)
        self.update_timestamp()

    def get_metadata(self) -> Optional[dict]:
        """
        Get metadata as dictionary.

        Returns:
            Dictionary containing client metadata, or None if not set
        """
        if self.client_metadata:
            try:
                return json.loads(self.metadata)
            except json.JSONDecodeError:
                return None
        return None

    def is_expired(self) -> bool:
        """
        Check if token has expired.

        Returns:
            True if current time > expires_at, False otherwise
        """
        current_time = self._get_current_timestamp()
        return current_time > self.expires_at

    def is_used(self) -> bool:
        """
        Check if token has been used.

        Returns:
            True if used_at is set, False otherwise
        """
        return self.used_at is not None

    def is_valid(self) -> bool:
        """
        Check if token is valid (not expired, not used, not deleted).

        Returns:
            True if token is valid, False otherwise
        """
        return not self.is_expired() and not self.is_used() and not self.is_deleted()

    def mark_as_used(self) -> None:
        """
        Mark the token as used.

        Sets used_at timestamp to current time and soft deletes the token.
        """
        self.used_at = self._get_current_timestamp()
        self.soft_delete()  # Soft delete after use

    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """
        Convert to dictionary with additional computed fields.

        Args:
            exclude: Fields to exclude (token_hash always excluded)

        Returns:
            Dictionary representation
        """
        # Always exclude token_hash for security
        if exclude is None:
            exclude = []
        exclude.append("token_hash")

        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["is_expired"] = self.is_expired()
        data["is_used"] = self.is_used()
        data["is_valid"] = self.is_valid()
        data["is_deleted"] = self.is_deleted()

        return data

    def __repr__(self) -> str:
        """String representation."""
        status = "USED" if self.is_used() else "EXPIRED" if self.is_expired() else "VALID"
        deleted = " (DELETED)" if self.is_deleted() else ""
        return (
            f"<PasswordResetToken(id={self.id!r}, user_id={self.user_id!r}, "
            f"status={status}){deleted}>"
        )

