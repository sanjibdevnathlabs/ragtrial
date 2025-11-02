"""
OAuth Provider entity model.

Represents third-party OAuth login providers (Google, GitHub, etc.) for users.
"""

import json
import uuid
from typing import Optional

from sqlalchemy import Column, String, Text

import constants
from database.base_model import BaseModel


class OAuthProvider(BaseModel):
    """
    OAuth provider entity for third-party authentication.

    Stores information about a user's OAuth login provider (Google, GitHub, etc.).
    A user can have multiple OAuth providers linked to their account.

    Fields:
        id: UUID primary key
        user_id: Foreign key to users table (application-level)
        provider: OAuth provider name ('google', 'github')
        provider_user_id: User ID from the OAuth provider (unique per provider)
        email: Email associated with the OAuth account
        raw_data: Raw JSON data returned by the OAuth provider
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Indexes:
        - idx_oauth_providers_user_id: For fast lookup of user's OAuth accounts
        - idx_oauth_providers_provider: For querying by provider
        - idx_oauth_providers_provider_user_id: For fast lookup by provider's user ID
        - unique_provider_account: Ensures user can only have one account per provider
        - idx_oauth_providers_deleted_at: For filtering active vs deleted records

    Relationships:
        - user: Many-to-one with User (via user_id)
    """

    __tablename__ = constants.DB_TABLE_OAUTH_PROVIDERS

    # Override table name from base model
    __table_args__ = {"extend_existing": True}

    # OAuth provider-specific fields
    user_id = Column(String(36), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    provider_user_id = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    raw_data = Column(Text, nullable=True)

    @staticmethod
    def generate_id() -> str:
        """
        Generate a new UUID for OAuth provider ID.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    def set_raw_data(self, data: dict) -> None:
        """
        Set raw OAuth data as JSON string.

        Args:
            data: Dictionary containing OAuth provider response data
        """
        self.raw_data = json.dumps(data)
        self.update_timestamp()

    def get_raw_data(self) -> Optional[dict]:
        """
        Get raw OAuth data as dictionary.

        Returns:
            Dictionary containing OAuth provider data, or None if not set
        """
        if self.raw_data:
            try:
                return json.loads(self.raw_data)
            except json.JSONDecodeError:
                return None
        return None

    def is_google(self) -> bool:
        """
        Check if this is a Google OAuth provider.

        Returns:
            True if provider is Google
        """
        return self.provider == constants.OAUTH_PROVIDER_GOOGLE

    def is_github(self) -> bool:
        """
        Check if this is a GitHub OAuth provider.

        Returns:
            True if provider is GitHub
        """
        return self.provider == constants.OAUTH_PROVIDER_GITHUB

    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """
        Convert to dictionary with additional computed fields.

        Args:
            exclude: Fields to exclude (raw_data excluded by default for brevity)

        Returns:
            Dictionary representation
        """
        # Exclude raw_data by default (can be large)
        if exclude is None:
            exclude = []
        if "raw_data" not in exclude:
            exclude.append("raw_data")

        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["is_deleted"] = self.is_deleted()
        data["provider_display_name"] = self.provider.capitalize()

        return data

    def __repr__(self) -> str:
        """String representation."""
        deleted = " (DELETED)" if self.is_deleted() else ""
        return (
            f"<OAuthProvider(id={self.id!r}, user_id={self.user_id!r}, "
            f"provider={self.provider!r}, provider_user_id={self.provider_user_id!r})"
            f"{deleted}>"
        )

