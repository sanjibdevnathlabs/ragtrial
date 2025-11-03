"""
Create user_permissions table

Generated at: 2025-11-02 21:39:39

Creates the user_permissions mapping table for RBAC system.
This allows direct permission assignments to users (overrides role permissions).

Schema:
- id: VARCHAR(36) - UUID primary key
- user_id: VARCHAR(36) - References users.id (application-level)
- permission_id: VARCHAR(36) - References permissions.id (application-level)
- granted_by: VARCHAR(36) - User ID who granted this permission (NULL = system)
- granted_at: BIGINT - Grant timestamp (milliseconds)
- expires_at: BIGINT - Expiration timestamp (NULL = never expires)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_user_permissions_user_id: Fast lookup by user
- idx_user_permissions_permission_id: Fast lookup by permission
- idx_user_permissions_user_permission: Composite lookup
- idx_user_permissions_deleted_at: Filter active mappings
- unique_user_permission: Prevent duplicate assignments
"""

from sqlalchemy import text


def up(connection):
    """Apply migration - Create user_permissions table."""
    connection.execute(
        text(
            """
        CREATE TABLE user_permissions (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL COMMENT 'References users.id',
            permission_id VARCHAR(36) NOT NULL COMMENT 'References permissions.id',
            granted_by VARCHAR(36) DEFAULT NULL COMMENT 'User ID who granted this permission (NULL = system)',
            granted_at BIGINT NOT NULL COMMENT 'Grant timestamp (milliseconds)',
            expires_at BIGINT DEFAULT NULL COMMENT 'Expiration timestamp (NULL = never)',
            created_at BIGINT NOT NULL COMMENT 'Creation timestamp (milliseconds)',
            updated_at BIGINT NOT NULL COMMENT 'Last update timestamp (milliseconds)',
            deleted_at BIGINT DEFAULT NULL COMMENT 'Soft delete timestamp (milliseconds)',
            INDEX idx_user_permissions_user_id (user_id),
            INDEX idx_user_permissions_permission_id (permission_id),
            INDEX idx_user_permissions_user_permission (user_id, permission_id),
            INDEX idx_user_permissions_deleted_at (deleted_at),
            UNIQUE KEY unique_user_permission (user_id, permission_id, deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='User-Permission direct assignments for RBAC system'
    """
        )
    )


def down(connection):
    """Rollback migration - Drop user_permissions table."""
    connection.execute(text("DROP TABLE IF EXISTS user_permissions"))
