"""
Create Password Reset Tokens Table

Generated at: 2025-11-02 (Phase 1: Authentication)

This migration creates the 'password_reset_tokens' table for password reset flow.

Schema:
- id: VARCHAR(36) - UUID primary key
- user_id: VARCHAR(36) - Reference to users table (application-level FK)
- token_hash: VARCHAR(64) - SHA-256 hash of reset token (unique, indexed)
- metadata: TEXT - JSON containing user_agent, ip_address, request_source
- expires_at: BIGINT - Expiration timestamp (milliseconds, default 30 minutes)
- used_at: BIGINT - Timestamp when token was used (NULL = unused)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_reset_token_hash: Fast token lookup (unique)
- idx_reset_user_id: Query user's reset tokens
- idx_reset_expires_at: Cleanup expired tokens
- idx_reset_used_at: Filter used vs unused tokens
- idx_reset_deleted_at: Filter active vs deleted tokens

Metadata JSON Structure:
{
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1",
    "request_source": "forgot_password_page|admin_panel",
    "requested_at": 1698765432123
}

Business Logic (handled in code):
- Only ONE active (unused + non-expired) reset token per user
- When new reset token is requested, previous active tokens are soft-deleted
- Tokens expire after 30 minutes (configurable)
- After token is used, it's marked with used_at timestamp
- Used tokens cannot be reused (checked in code)

Note: Soft delete pattern allows audit trail of all password reset attempts.
This is important for security monitoring and compliance.
"""

from sqlalchemy import text


def up(connection):
    """
    Apply migration - Create password_reset_tokens table.

    Args:
        connection: SQLAlchemy connection object
    """
    # Create password_reset_tokens table
    connection.execute(
        text(
            """
        CREATE TABLE password_reset_tokens (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            token_hash VARCHAR(64) NOT NULL,
            metadata TEXT NULL,
            expires_at BIGINT NOT NULL,
            used_at BIGINT NULL,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            deleted_at BIGINT NULL,
            CONSTRAINT unique_reset_token_hash UNIQUE (token_hash)
        )
    """
        )
    )
    connection.commit()

    # Create indexes
    connection.execute(
        text(
            "CREATE INDEX idx_reset_token_hash ON password_reset_tokens(token_hash)"
        )
    )
    connection.execute(
        text("CREATE INDEX idx_reset_user_id ON password_reset_tokens(user_id)")
    )
    connection.execute(
        text("CREATE INDEX idx_reset_expires_at ON password_reset_tokens(expires_at)")
    )
    connection.execute(
        text("CREATE INDEX idx_reset_used_at ON password_reset_tokens(used_at)")
    )
    connection.execute(
        text("CREATE INDEX idx_reset_deleted_at ON password_reset_tokens(deleted_at)")
    )
    connection.commit()


def down(connection):
    """
    Rollback migration - Drop password_reset_tokens table.

    Args:
        connection: SQLAlchemy connection object
    """
    connection.execute(text("DROP TABLE IF EXISTS password_reset_tokens"))
    connection.commit()

