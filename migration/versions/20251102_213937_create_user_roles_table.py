"""
Create user_roles table

Generated at: 2025-11-02 21:39:37

Creates the user_roles mapping table for RBAC system.

Schema:
- id: VARCHAR(36) - UUID primary key
- user_id: VARCHAR(36) - References users.id (application-level)
- role_id: VARCHAR(36) - References roles.id (application-level)
- granted_by: VARCHAR(36) - User ID who granted this role (NULL = system)
- granted_at: BIGINT - Grant timestamp (milliseconds)
- expires_at: BIGINT - Expiration timestamp (NULL = never expires)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_user_roles_user_id: Fast lookup by user
- idx_user_roles_role_id: Fast lookup by role
- idx_user_roles_user_role: Composite lookup
- idx_user_roles_deleted_at: Filter active mappings
- unique_user_role: Prevent duplicate assignments
"""

from sqlalchemy import text


def up(connection):
    """Apply migration - Create user_roles table."""
    connection.execute(
        text(
            """
        CREATE TABLE user_roles (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL COMMENT 'References users.id',
            role_id VARCHAR(36) NOT NULL COMMENT 'References roles.id',
            granted_by VARCHAR(36) DEFAULT NULL COMMENT 'User ID who granted this role (NULL = system)',
            granted_at BIGINT NOT NULL COMMENT 'Grant timestamp (milliseconds)',
            expires_at BIGINT DEFAULT NULL COMMENT 'Expiration timestamp (NULL = never)',
            created_at BIGINT NOT NULL COMMENT 'Creation timestamp (milliseconds)',
            updated_at BIGINT NOT NULL COMMENT 'Last update timestamp (milliseconds)',
            deleted_at BIGINT DEFAULT NULL COMMENT 'Soft delete timestamp (milliseconds)',
            INDEX idx_user_roles_user_id (user_id),
            INDEX idx_user_roles_role_id (role_id),
            INDEX idx_user_roles_user_role (user_id, role_id),
            INDEX idx_user_roles_deleted_at (deleted_at),
            UNIQUE KEY unique_user_role (user_id, role_id, deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='User-Role mappings for RBAC system'
    """
        )
    )


def down(connection):
    """Rollback migration - Drop user_roles table."""
    connection.execute(text("DROP TABLE IF EXISTS user_roles"))
