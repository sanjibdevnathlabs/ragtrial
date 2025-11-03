"""
Create Refresh Tokens Table

Generated at: 2025-11-02 (Phase 1: Authentication)

This migration creates the 'refresh_tokens' table for JWT refresh token management.

Schema:
- id: VARCHAR(36) - UUID primary key
- user_id: VARCHAR(36) - Reference to users table (application-level FK)
- token_hash: VARCHAR(64) - SHA-256 hash of refresh token (unique, indexed)
- metadata: TEXT - JSON containing user_agent, ip_address, device_info
- expires_at: BIGINT - Expiration timestamp (milliseconds)
- revoked_at: BIGINT - Revocation timestamp (NULL = active)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_refresh_token_hash: Fast token lookup (unique)
- idx_refresh_user_id: Query user's refresh tokens
- idx_refresh_expires_at: Cleanup expired tokens
- idx_refresh_revoked_at: Filter active vs revoked tokens
- idx_refresh_deleted_at: Filter active vs deleted tokens

Metadata JSON Structure:
{
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1",
    "device_type": "desktop|mobile|tablet",
    "os": "Windows|MacOS|Linux|iOS|Android",
    "browser": "Chrome|Firefox|Safari|Edge"
}

Note: Refresh tokens are long-lived (30 days default). They are used to obtain
new access tokens without re-authentication. Each user can have multiple active
refresh tokens (one per device/session).
"""

from sqlalchemy import text


def up(connection):
    """
    Apply migration - Create refresh_tokens table.

    Args:
        connection: SQLAlchemy connection object
    """
    # Create refresh_tokens table
    connection.execute(
        text(
            """
        CREATE TABLE refresh_tokens (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            token_hash VARCHAR(64) NOT NULL,
            metadata TEXT NULL,
            expires_at BIGINT NOT NULL,
            revoked_at BIGINT NULL,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            deleted_at BIGINT NULL,
            CONSTRAINT unique_token_hash UNIQUE (token_hash)
        )
    """
        )
    )
    connection.commit()

    # Create indexes
    connection.execute(
        text("CREATE INDEX idx_refresh_token_hash ON refresh_tokens(token_hash)")
    )
    connection.execute(
        text("CREATE INDEX idx_refresh_user_id ON refresh_tokens(user_id)")
    )
    connection.execute(
        text("CREATE INDEX idx_refresh_expires_at ON refresh_tokens(expires_at)")
    )
    connection.execute(
        text("CREATE INDEX idx_refresh_revoked_at ON refresh_tokens(revoked_at)")
    )
    connection.execute(
        text("CREATE INDEX idx_refresh_deleted_at ON refresh_tokens(deleted_at)")
    )
    connection.commit()


def down(connection):
    """
    Rollback migration - Drop refresh_tokens table.

    Args:
        connection: SQLAlchemy connection object
    """
    connection.execute(text("DROP TABLE IF EXISTS refresh_tokens"))
    connection.commit()

