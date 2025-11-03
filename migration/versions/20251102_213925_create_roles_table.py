"""
Create roles table

Generated at: 2025-11-02 21:39:25

Creates the roles table for RBAC system.

Schema:
- id: VARCHAR(36) - UUID primary key
- name: VARCHAR(50) - Role name (unique, e.g., 'admin', 'user')
- description: TEXT - Human-readable description
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_roles_name: Fast role lookup by name
- idx_roles_deleted_at: Filter active roles
"""

from sqlalchemy import text


def up(connection):
    """Apply migration - Create roles table."""
    connection.execute(
        text(
            """
        CREATE TABLE roles (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE COMMENT 'Role name (admin, user, etc.)',
            description TEXT COMMENT 'Human-readable description',
            created_at BIGINT NOT NULL COMMENT 'Creation timestamp (milliseconds)',
            updated_at BIGINT NOT NULL COMMENT 'Last update timestamp (milliseconds)',
            deleted_at BIGINT DEFAULT NULL COMMENT 'Soft delete timestamp (milliseconds)',
            INDEX idx_roles_name (name),
            INDEX idx_roles_deleted_at (deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Roles for RBAC system'
    """
        )
    )


def down(connection):
    """Rollback migration - Drop roles table."""
    connection.execute(text("DROP TABLE IF EXISTS roles"))
