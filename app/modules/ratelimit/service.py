"""
Rate limiting service.

Single responsibility: Rate limit checking and enforcement.
"""

from typing import Optional, Tuple

from app.modules.ratelimit.config_service import RateLimitConfigService
from app.modules.ratelimit.storage.base import RateLimitStorageProtocol
from app.modules.ratelimit.storage.factory import create_storage
from config import Config
from logger import get_logger

logger = get_logger(__name__)


class RateLimitService:
    """
    Rate limiting service.

    Responsibilities:
    - Check if request is within rate limit
    - Track request counts per route and client
    - Provide rate limit headers info

    Configuration priority:
    1. Database (runtime-configurable)
    2. TOML config (fallback)

    Storage:
    - Automatically selects Memory or Redis based on config
    """

    def __init__(self, storage: Optional[RateLimitStorageProtocol] = None):
        """
        Initialize rate limit service.

        Args:
            storage: Storage backend (defaults to factory-created storage based on config)
        """
        self.config = Config()
        self.config_service = RateLimitConfigService()
        self.storage = storage or create_storage()

    def get_route_config_with_strategy(self, route_name: str) -> dict:
        """
        Get rate limit config including key_strategy for a route.

        Configuration priority:
        1. Database config (runtime-configurable)
        2. Global database default
        3. TOML config (fallback)

        Args:
            route_name: Route name (e.g., "auth_login")

        Returns:
            Dict with keys: requests, window_seconds, key_strategy, enabled
        """
        # Try to get config from database first
        db_config = self.config_service.get_route_config(route_name)

        if db_config:
            # Use database config (priority 1)
            return {
                "requests": db_config["requests"],
                "window_seconds": db_config["window_seconds"],
                "key_strategy": db_config.get("key_strategy", "ip"),
                "enabled": db_config.get("enabled", True),
            }

        # Fall back to TOML config (priority 3)
        requests_limit, window_seconds = self.config.ratelimit.get_route_limit(
            route_name
        )

        return {
            "requests": requests_limit,
            "window_seconds": window_seconds,
            "key_strategy": "ip",  # Default to IP for TOML config
            "enabled": self.config.ratelimit.is_route_enabled(route_name),
        }

    def check_rate_limit(
        self,
        route_name: str,
        client_id: str,
    ) -> Tuple[bool, dict]:
        """
        Check if request is within rate limit.

        Configuration priority:
        1. Database config (runtime-configurable)
        2. TOML config (fallback)

        Args:
            route_name: Route name (e.g., "auth_login")
            client_id: Client identifier (already built based on strategy)

        Returns:
            Tuple of (is_allowed, headers_info)
            headers_info contains: limit, remaining, window
        """
        # Check if rate limiting is enabled globally in TOML
        if not self.config.ratelimit.enabled:
            return True, {}

        # Get route config
        route_config = self.get_route_config_with_strategy(route_name)

        if not route_config.get("enabled", True):
            return True, {}

        requests_limit = route_config["requests"]
        window_seconds = route_config["window_seconds"]

        # Generate storage key
        key = f"{route_name}:{client_id}"

        # Increment and get count
        current_count = self.storage.increment(key, window_seconds)

        # Check if exceeded
        is_allowed = current_count <= requests_limit
        remaining = max(0, requests_limit - current_count)

        # Prepare headers info
        headers_info = {
            "limit": requests_limit,
            "remaining": remaining,
            "window": window_seconds,
        }

        if not is_allowed:
            logger.warning(
                "rate_limit_exceeded",
                route_name=route_name,
                client_id=client_id,
                count=current_count,
                limit=requests_limit,
            )

        return is_allowed, headers_info

    def reset_client_limit(self, route_name: str, client_id: str) -> None:
        """
        Reset rate limit for specific client on route.

        Args:
            route_name: Route name
            client_id: Client identifier
        """
        key = f"{route_name}:{client_id}"
        self.storage.reset(key)

    def get_client_usage(
        self, route_name: str, client_id: str
    ) -> Tuple[int, int, int]:
        """
        Get current usage for client on route.

        Args:
            route_name: Route name
            client_id: Client identifier

        Returns:
            Tuple of (current_count, limit, window_seconds)
        """
        requests_limit, window_seconds = self.config.ratelimit.get_route_limit(
            route_name
        )

        key = f"{route_name}:{client_id}"
        current_count = self.storage.get_count(key, window_seconds)

        return current_count, requests_limit, window_seconds

    def cleanup_expired(self) -> int:
        """
        Cleanup expired rate limit entries.

        Returns:
            Number of entries removed
        """
        return self.storage.cleanup()

