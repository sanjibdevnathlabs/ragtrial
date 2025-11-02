"""
Create role_permissions table

Generated at: 2025-11-02 21:39:38

Creates the role_permissions mapping table for RBAC system.

Schema:
- id: VARCHAR(36) - UUID primary key
- role_id: VARCHAR(36) - References roles.id (application-level)
- permission_id: VARCHAR(36) - References permissions.id (application-level)
- granted_by: VARCHAR(36) - User ID who granted this permission (NULL = system)
- granted_at: BIGINT - Grant timestamp (milliseconds)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_role_permissions_role_id: Fast lookup by role
- idx_role_permissions_permission_id: Fast lookup by permission
- idx_role_permissions_role_permission: Composite lookup
- idx_role_permissions_deleted_at: Filter active mappings
- unique_role_permission: Prevent duplicate assignments
"""

from sqlalchemy import text


def up(connection):
    """Apply migration - Create role_permissions table."""
    connection.execute(
        text(
            """
        CREATE TABLE role_permissions (
            id VARCHAR(36) PRIMARY KEY,
            role_id VARCHAR(36) NOT NULL COMMENT 'References roles.id',
            permission_id VARCHAR(36) NOT NULL COMMENT 'References permissions.id',
            granted_by VARCHAR(36) DEFAULT NULL COMMENT 'User ID who granted this permission (NULL = system)',
            granted_at BIGINT NOT NULL COMMENT 'Grant timestamp (milliseconds)',
            created_at BIGINT NOT NULL COMMENT 'Creation timestamp (milliseconds)',
            updated_at BIGINT NOT NULL COMMENT 'Last update timestamp (milliseconds)',
            deleted_at BIGINT DEFAULT NULL COMMENT 'Soft delete timestamp (milliseconds)',
            INDEX idx_role_permissions_role_id (role_id),
            INDEX idx_role_permissions_permission_id (permission_id),
            INDEX idx_role_permissions_role_permission (role_id, permission_id),
            INDEX idx_role_permissions_deleted_at (deleted_at),
            UNIQUE KEY unique_role_permission (role_id, permission_id, deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Role-Permission mappings for RBAC system'
    """
        )
    )


def down(connection):
    """Rollback migration - Drop role_permissions table."""
    connection.execute(text("DROP TABLE IF EXISTS role_permissions"))
