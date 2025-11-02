"""
Create rate_limit_configs table.

This table stores runtime-configurable rate limits for API routes.
Supports global defaults and route-specific overrides.

Revision: 20251102_195624
"""

from sqlalchemy import text


def up(connection):
    """Create rate_limit_configs table."""
    # Create rate_limit_configs table

    connection.execute(
        text(
            """
        CREATE TABLE rate_limit_configs (
            id VARCHAR(36) PRIMARY KEY,
            route_name VARCHAR(255) NOT NULL COMMENT 'Route name (use "global" for global default)',
            requests INT NOT NULL COMMENT 'Number of requests allowed',
            window_seconds INT NOT NULL COMMENT 'Time window in seconds',
            enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Enable/disable this limit',
            key_strategy VARCHAR(50) NOT NULL DEFAULT 'ip' COMMENT 'Rate limit key strategy: ip, user, session, route, ip_and_route, user_and_route',
            description TEXT COMMENT 'Human-readable description of this limit',
            created_at BIGINT NOT NULL COMMENT 'Creation timestamp (milliseconds)',
            updated_at BIGINT NOT NULL COMMENT 'Last update timestamp (milliseconds)',
            deleted_at BIGINT DEFAULT NULL COMMENT 'Soft delete timestamp (milliseconds)',
            INDEX idx_rate_limit_route_name (route_name),
            INDEX idx_rate_limit_enabled (enabled),
            INDEX idx_rate_limit_deleted_at (deleted_at),
            UNIQUE KEY unique_route_name (route_name, deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Runtime-configurable rate limits for API routes'
    """
        )
    )

    # Insert global default
    connection.execute(
        text(
            """
        INSERT INTO rate_limit_configs 
            (id, route_name, requests, window_seconds, enabled, key_strategy, description, created_at, updated_at)
        VALUES 
            (
                UUID(),
                'global',
                100,
                60,
                1,
                'ip',
                'Global default rate limit applies to all routes unless overridden',
                UNIX_TIMESTAMP() * 1000,
                UNIX_TIMESTAMP() * 1000
            )
    """
        )
    )

    # Insert auth route defaults (public endpoints use IP-based rate limiting)
    connection.execute(
        text(
            """
        INSERT INTO rate_limit_configs 
            (id, route_name, requests, window_seconds, enabled, key_strategy, description, created_at, updated_at)
        VALUES 
            (UUID(), 'auth_register', 5, 3600, 1, 'ip', 'Registration limit - 5 per hour per IP to prevent spam', UNIX_TIMESTAMP() * 1000, UNIX_TIMESTAMP() * 1000),
            (UUID(), 'auth_login', 10, 300, 1, 'ip', 'Login limit - 10 per 5 minutes per IP to prevent brute force', UNIX_TIMESTAMP() * 1000, UNIX_TIMESTAMP() * 1000),
            (UUID(), 'auth_refresh', 50, 3600, 1, 'user', 'Token refresh limit - 50 per hour per user', UNIX_TIMESTAMP() * 1000, UNIX_TIMESTAMP() * 1000),
            (UUID(), 'auth_logout', 20, 3600, 1, 'user', 'Logout limit - 20 per hour per user', UNIX_TIMESTAMP() * 1000, UNIX_TIMESTAMP() * 1000),
            (UUID(), 'auth_password_change', 5, 3600, 1, 'user', 'Password change limit - 5 per hour per user', UNIX_TIMESTAMP() * 1000, UNIX_TIMESTAMP() * 1000),
            (UUID(), 'auth_password_reset_request', 3, 3600, 1, 'ip', 'Password reset request limit - 3 per hour per IP to prevent email spam', UNIX_TIMESTAMP() * 1000, UNIX_TIMESTAMP() * 1000),
            (UUID(), 'auth_password_reset_confirm', 5, 3600, 1, 'ip', 'Password reset confirm limit - 5 per hour per IP', UNIX_TIMESTAMP() * 1000, UNIX_TIMESTAMP() * 1000)
    """
        )
    )


def down(connection):
    """Drop rate_limit_configs table."""
    connection.execute(text("DROP TABLE IF EXISTS rate_limit_configs"))
