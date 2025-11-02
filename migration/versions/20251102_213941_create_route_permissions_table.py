"""
Create route_permissions table

Generated at: 2025-11-02 21:39:41

Creates the route_permissions table for centralized route permission configuration.
Similar to rate_limit_configs, this allows runtime configuration of which permissions
are required for each API endpoint.

Schema:
- id: VARCHAR(36) - UUID primary key
- route_name: VARCHAR(255) - Route identifier (e.g., 'admin_users_list', 'rate_limits_update')
- http_method: VARCHAR(10) - HTTP method (GET, POST, PUT, DELETE, etc.)
- route_path: VARCHAR(500) - API path (e.g., '/api/v1/admin/users')
- required_permissions: TEXT - JSON array of required permission names (e.g., '["user:read", "user:list"]')
- description: TEXT - Human-readable description
- enabled: TINYINT(1) - Enable/disable this route protection
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_route_permissions_route_name: Fast lookup by route name
- idx_route_permissions_enabled: Filter enabled routes
- idx_route_permissions_deleted_at: Filter active routes
- unique_route_name: Prevent duplicate route configurations
"""

from sqlalchemy import text


def up(connection):
    """Apply migration - Create route_permissions table."""
    connection.execute(
        text(
            """
        CREATE TABLE route_permissions (
            id VARCHAR(36) PRIMARY KEY,
            route_name VARCHAR(255) NOT NULL COMMENT 'Route identifier (admin_users_list, etc.)',
            http_method VARCHAR(10) NOT NULL COMMENT 'HTTP method (GET, POST, PUT, DELETE)',
            route_path VARCHAR(500) NOT NULL COMMENT 'API path (/api/v1/admin/users)',
            required_permissions TEXT NOT NULL COMMENT 'JSON array of required permission names',
            description TEXT COMMENT 'Human-readable description',
            enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Enable/disable route protection',
            created_at BIGINT NOT NULL COMMENT 'Creation timestamp (milliseconds)',
            updated_at BIGINT NOT NULL COMMENT 'Last update timestamp (milliseconds)',
            deleted_at BIGINT DEFAULT NULL COMMENT 'Soft delete timestamp (milliseconds)',
            INDEX idx_route_permissions_route_name (route_name),
            INDEX idx_route_permissions_enabled (enabled),
            INDEX idx_route_permissions_deleted_at (deleted_at),
            UNIQUE KEY unique_route_name (route_name, deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Centralized route permission configuration'
    """
        )
    )


def down(connection):
    """Rollback migration - Drop route_permissions table."""
    connection.execute(text("DROP TABLE IF EXISTS route_permissions"))
