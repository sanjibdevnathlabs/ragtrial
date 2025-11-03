"""
Rate limit configuration management service.

Single responsibility: CRUD operations for rate limit configurations.
"""

import trace.codes as codes
from typing import Dict, List, Optional

from app.modules.ratelimit.entity import RateLimitConfig
from app.modules.ratelimit.repository import RateLimitConfigRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class RateLimitConfigService:
    """
    Rate limit configuration management service.

    Responsibilities:
    - CRUD operations for rate limit configs
    - Get rate limit for specific route
    - Get global default
    - Enable/disable rate limits
    """

    def __init__(self):
        """Initialize config service."""
        self.repository = RateLimitConfigRepository()
        self.session_factory = SessionFactory()

    def get_route_config(self, route_name: str) -> Optional[Dict]:
        """
        Get rate limit config for route.

        Falls back to global default if route-specific config not found.

        Args:
            route_name: Route name

        Returns:
            Config dict or None
        """
        with self.session_factory.get_read_session() as session:
            # Try route-specific first
            config = self.repository.find_by_route_name(session, route_name)

            if config and config.is_enabled():
                return config.to_dict()

            # Fall back to global default
            global_config = self.repository.find_global_default(session)

            if global_config and global_config.is_enabled():
                return global_config.to_dict()

            return None

    def get_all_configs(self) -> List[Dict]:
        """
        Get all rate limit configs.

        Returns:
            List of config dicts
        """
        with self.session_factory.get_read_session() as session:
            configs = self.repository.find_all(session)
            return [c.to_dict() for c in configs]

    def create_config(
        self,
        route_name: str,
        requests: int,
        window_seconds: int,
        enabled: bool = True,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Create new rate limit config.

        Args:
            route_name: Route name (use "global" for global default)
            requests: Number of requests allowed
            window_seconds: Time window in seconds
            enabled: Enable this limit
            description: Human-readable description

        Returns:
            Created config dict

        Raises:
            ValueError: If route config already exists
        """
        logger.info(
            codes.DB_REPOSITORY_STARTED,
            operation="create_rate_limit_config",
            route_name=route_name,
        )

        # Check if exists
        with self.session_factory.get_read_session() as session:
            existing = self.repository.find_by_route_name(session, route_name)

            if existing:
                raise ValueError(f"Rate limit config for '{route_name}' already exists")

        # Create
        config = RateLimitConfig(
            id=RateLimitConfig.generate_id(),
            route_name=route_name,
            requests=requests,
            window_seconds=window_seconds,
            enabled=1 if enabled else 0,
            description=description,
        )

        with self.session_factory.get_write_session() as session:
            created = self.repository.create(session, config)

        logger.info(
            codes.DB_REPOSITORY_COMPLETED,
            operation="create_rate_limit_config",
            route_name=route_name,
        )

        return created.to_dict()

    def update_config(
        self,
        route_name: str,
        requests: Optional[int] = None,
        window_seconds: Optional[int] = None,
        enabled: Optional[bool] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Update rate limit config.

        Args:
            route_name: Route name
            requests: New requests limit
            window_seconds: New window
            enabled: Enable/disable
            description: New description

        Returns:
            Updated config dict or None if not found
        """
        with self.session_factory.get_write_session() as session:
            config = self.repository.find_by_route_name(session, route_name)

            if not config:
                logger.warning(codes.DB_ENTITY_NOT_FOUND, route_name=route_name)
                return None

            # Update fields
            if requests is not None:
                config.requests = requests

            if window_seconds is not None:
                config.window_seconds = window_seconds

            if enabled is not None:
                config.enabled = 1 if enabled else 0

            if description is not None:
                config.description = description

            updated = self.repository.update(session, config)

        return updated.to_dict()

    def delete_config(self, route_name: str) -> bool:
        """
        Delete rate limit config (soft delete).

        Args:
            route_name: Route name

        Returns:
            True if deleted, False if not found
        """
        with self.session_factory.get_read_session() as session:
            config = self.repository.find_by_route_name(session, route_name)

            if not config:
                return False

            config_id = config.id

        with self.session_factory.get_write_session() as session:
            return self.repository.soft_delete(session, config_id)

    def enable_route(self, route_name: str) -> bool:
        """Enable rate limit for route."""
        with self.session_factory.get_write_session() as session:
            return self.repository.enable_route(session, route_name)

    def disable_route(self, route_name: str) -> bool:
        """Disable rate limit for route."""
        with self.session_factory.get_write_session() as session:
            return self.repository.disable_route(session, route_name)

