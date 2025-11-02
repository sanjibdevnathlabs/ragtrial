"""
Create permissions table

Generated at: 2025-11-02 21:39:36

Creates the permissions table for RBAC system.

Schema:
- id: VARCHAR(36) - UUID primary key
- name: VARCHAR(100) - Permission name (unique, e.g., 'user:read', 'rate_limit:write')
- resource: VARCHAR(50) - Resource type (user, role, permission, rate_limit, file, etc.)
- action: VARCHAR(50) - Action (read, write, delete, manage, etc.)
- description: TEXT - Human-readable description
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_permissions_name: Fast permission lookup by name
- idx_permissions_resource: Filter by resource
- idx_permissions_resource_action: Composite lookup
- idx_permissions_deleted_at: Filter active permissions
"""

from sqlalchemy import text


def up(connection):
    """Apply migration - Create permissions table."""
    connection.execute(
        text(
            """
        CREATE TABLE permissions (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Permission name (resource:action, e.g., user:read)',
            resource VARCHAR(50) NOT NULL COMMENT 'Resource type (user, role, permission, rate_limit, file)',
            action VARCHAR(50) NOT NULL COMMENT 'Action (read, write, delete, manage)',
            description TEXT COMMENT 'Human-readable description',
            created_at BIGINT NOT NULL COMMENT 'Creation timestamp (milliseconds)',
            updated_at BIGINT NOT NULL COMMENT 'Last update timestamp (milliseconds)',
            deleted_at BIGINT DEFAULT NULL COMMENT 'Soft delete timestamp (milliseconds)',
            INDEX idx_permissions_name (name),
            INDEX idx_permissions_resource (resource),
            INDEX idx_permissions_resource_action (resource(20), action(20)),
            INDEX idx_permissions_deleted_at (deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Permissions for RBAC system'
    """
        )
    )


def down(connection):
    """Rollback migration - Drop permissions table."""
    connection.execute(text("DROP TABLE IF EXISTS permissions"))
