"""
Create Users Table

Generated at: 2025-11-02 (Phase 1: Authentication)

This migration creates the 'users' table for user account management.

Schema:
- id: VARCHAR(36) - UUID primary key
- email: VARCHAR(255) - User email (unique, indexed, used for login)
- password_hash: VARCHAR(255) - Bcrypt password hash (NULL for social-only users)
- full_name: VARCHAR(255) - User's full name (e.g., "John Doe")
- avatar_url: VARCHAR(512) - Profile picture URL (optional)
- is_verified: BOOLEAN - Email verification status (required for actions)
- email_verified_at: BIGINT - Timestamp when email was verified (milliseconds)
- status: VARCHAR(20) - Account status (active, inactive, suspended)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_users_email: Fast login lookup (unique)
- idx_users_status: Filter by account status
- idx_users_is_verified: Query verified vs unverified users
- idx_users_deleted_at: Filter active vs deleted users

Note: This table supports both local authentication (email/password) and OAuth.
For OAuth-only users, password_hash will be NULL.
"""

from sqlalchemy import text


def up(connection):
    """
    Apply migration - Create users table.

    Args:
        connection: SQLAlchemy connection object
    """
    # Create users table
    connection.execute(
        text(
            """
        CREATE TABLE users (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NULL,
            full_name VARCHAR(255) NOT NULL,
            avatar_url VARCHAR(512) NULL,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            email_verified_at BIGINT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'inactive',
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            deleted_at BIGINT NULL,
            CONSTRAINT unique_email UNIQUE (email)
        )
    """
        )
    )
    connection.commit()

    # Create indexes
    connection.execute(text("CREATE INDEX idx_users_email ON users(email)"))
    connection.execute(text("CREATE INDEX idx_users_status ON users(status)"))
    connection.execute(
        text("CREATE INDEX idx_users_is_verified ON users(is_verified)")
    )
    connection.execute(text("CREATE INDEX idx_users_deleted_at ON users(deleted_at)"))
    connection.commit()


def down(connection):
    """
    Rollback migration - Drop users table.

    Args:
        connection: SQLAlchemy connection object
    """
    connection.execute(text("DROP TABLE IF EXISTS users"))
    connection.commit()

