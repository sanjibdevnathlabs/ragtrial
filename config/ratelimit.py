"""
Rate limit configuration.

Configures rate limiting per route with different storage backends.
"""

from typing import Dict, Optional


class RouteRateLimitConfig:
    """Rate limit configuration for a specific route."""

    def __init__(self, config_dict: Dict):
        """Initialize route rate limit config."""
        self.requests: int = config_dict.get("requests", 100)
        self.window_seconds: int = config_dict.get("window_seconds", 60)
        self.enabled: bool = config_dict.get("enabled", True)


class InMemoryStorageConfig:
    """In-memory storage configuration."""

    def __init__(self, config_dict: Dict):
        """Initialize in-memory storage config."""
        self.cleanup_interval_seconds: int = config_dict.get(
            "cleanup_interval_seconds", 3600
        )


class RedisStorageConfig:
    """Redis storage configuration."""

    def __init__(self, config_dict: Dict):
        """Initialize Redis storage config."""
        self.host: str = config_dict.get("host", "localhost")
        self.port: int = config_dict.get("port", 6379)
        self.db: int = config_dict.get("db", 0)
        self.password: str = config_dict.get("password", "")
        self.key_prefix: str = config_dict.get("key_prefix", "ratelimit")
        self.socket_timeout: int = config_dict.get("socket_timeout", 5)
        self.socket_connect_timeout: int = config_dict.get(
            "socket_connect_timeout", 5
        )
        self.max_connections: int = config_dict.get("max_connections", 50)


class RateLimitConfig:
    """
    Rate limit configuration.

    Manages global and per-route rate limiting settings.
    """

    def __init__(self, config_dict: Dict):
        """Initialize rate limit config."""
        self.enabled: bool = config_dict.get("enabled", True)
        self.storage: str = config_dict.get("storage", "memory")
        self.default_requests: int = config_dict.get("default_requests", 100)
        self.default_window_seconds: int = config_dict.get(
            "default_window_seconds", 60
        )

        # Storage configurations
        self.inmemory: InMemoryStorageConfig = InMemoryStorageConfig(
            config_dict.get("inmemory", {})
        )
        self.redis: RedisStorageConfig = RedisStorageConfig(
            config_dict.get("redis", {})
        )

        # Parse route-specific configurations
        self.routes: Dict[str, RouteRateLimitConfig] = {}
        routes_config = config_dict.get("routes", {})

        for route_name, route_config in routes_config.items():
            self.routes[route_name] = RouteRateLimitConfig(route_config)

    def get_route_config(self, route_name: str) -> Optional[RouteRateLimitConfig]:
        """
        Get rate limit config for a route.

        Args:
            route_name: Route name

        Returns:
            RouteRateLimitConfig or None if not configured
        """
        return self.routes.get(route_name)

    def get_route_limit(self, route_name: str) -> tuple[int, int]:
        """
        Get rate limit for a route (requests, window_seconds).

        Falls back to default if route not configured.

        Args:
            route_name: Route name

        Returns:
            Tuple of (requests, window_seconds)
        """
        route_config = self.get_route_config(route_name)

        if route_config:
            return route_config.requests, route_config.window_seconds

        return self.default_requests, self.default_window_seconds

    def is_route_enabled(self, route_name: str) -> bool:
        """
        Check if rate limiting is enabled for a route.

        Args:
            route_name: Route name

        Returns:
            True if enabled (checks both global and route-specific)
        """
        if not self.enabled:
            return False

        route_config = self.get_route_config(route_name)

        if route_config:
            return route_config.enabled

        return True  # Default to enabled if not explicitly configured

