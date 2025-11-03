"""
Create OAuth Providers Table

Generated at: 2025-11-02 (Phase 1: Authentication)

This migration creates the 'oauth_providers' table for social authentication.

Supports normalized OAuth login - a user can have multiple OAuth providers linked.

Schema:
- id: VARCHAR(36) - UUID primary key
- user_id: VARCHAR(36) - Reference to users table (application-level FK)
- provider: VARCHAR(50) - OAuth provider (google, github)
- provider_user_id: VARCHAR(255) - User ID from OAuth provider
- email: VARCHAR(255) - Email from OAuth provider
- raw_data: TEXT - Full JSON response from OAuth provider (for debugging/audit)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_oauth_user_id: Fast lookup of user's OAuth providers
- idx_oauth_provider: Filter by OAuth provider type
- idx_oauth_provider_user_id: Lookup by provider's user ID
- idx_oauth_composite: Composite index for (user_id, provider) queries
- idx_oauth_deleted_at: Filter active vs deleted providers

Constraints:
- unique_provider_account: Unique constraint on (provider, provider_user_id)
  Prevents duplicate linking of same OAuth account

Note: This table allows multiple OAuth providers per user (e.g., Google + GitHub).
The raw_data field stores the complete OAuth response for audit/debugging.
"""

from sqlalchemy import text


def up(connection):
    """
    Apply migration - Create oauth_providers table.

    Args:
        connection: SQLAlchemy connection object
    """
    # Create oauth_providers table
    connection.execute(
        text(
            """
        CREATE TABLE oauth_providers (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            provider VARCHAR(50) NOT NULL,
            provider_user_id VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            raw_data TEXT NULL,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            deleted_at BIGINT NULL,
            CONSTRAINT unique_provider_account UNIQUE (provider, provider_user_id)
        )
    """
        )
    )
    connection.commit()

    # Create indexes
    connection.execute(
        text("CREATE INDEX idx_oauth_user_id ON oauth_providers(user_id)")
    )
    connection.execute(
        text("CREATE INDEX idx_oauth_provider ON oauth_providers(provider)")
    )
    connection.execute(
        text(
            "CREATE INDEX idx_oauth_provider_user_id ON oauth_providers(provider_user_id)"
        )
    )
    connection.execute(
        text("CREATE INDEX idx_oauth_composite ON oauth_providers(user_id, provider)")
    )
    connection.execute(
        text("CREATE INDEX idx_oauth_deleted_at ON oauth_providers(deleted_at)")
    )
    connection.commit()


def down(connection):
    """
    Rollback migration - Drop oauth_providers table.

    Args:
        connection: SQLAlchemy connection object
    """
    connection.execute(text("DROP TABLE IF EXISTS oauth_providers"))
    connection.commit()

