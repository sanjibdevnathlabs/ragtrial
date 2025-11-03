"""
Rate limit configuration repository.

Database operations for rate limit configurations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.ratelimit.entity import RateLimitConfig
from database.base_repository import BaseRepository


class RateLimitConfigRepository(BaseRepository[RateLimitConfig]):
    """
    Repository for rate limit configurations.

    Handles database operations for runtime-configurable rate limits.
    """

    def __init__(self):
        """Initialize repository with RateLimitConfig entity."""
        super().__init__(RateLimitConfig)

    def find_by_route_name(
        self, session: Session, route_name: str
    ) -> Optional[RateLimitConfig]:
        """
        Find rate limit config by route name.

        Args:
            session: Database session
            route_name: Route name (e.g., "auth_login", "global")

        Returns:
            RateLimitConfig or None
        """
        return (
            session.query(RateLimitConfig)
            .filter(
                RateLimitConfig.route_name == route_name,
                RateLimitConfig.deleted_at.is_(None),
            )
            .first()
        )

    def find_global_default(self, session: Session) -> Optional[RateLimitConfig]:
        """
        Find global default rate limit.

        Args:
            session: Database session

        Returns:
            Global RateLimitConfig or None
        """
        return self.find_by_route_name(session, "global")

    def find_all_enabled(self, session: Session) -> List[RateLimitConfig]:
        """
        Find all enabled rate limit configs.

        Args:
            session: Database session

        Returns:
            List of enabled RateLimitConfig
        """
        return (
            session.query(RateLimitConfig)
            .filter(
                RateLimitConfig.enabled == 1,
                RateLimitConfig.deleted_at.is_(None),
            )
            .all()
        )

    def disable_route(self, session: Session, route_name: str) -> bool:
        """
        Disable rate limit for a route.

        Args:
            session: Database session
            route_name: Route name

        Returns:
            True if disabled, False if not found
        """
        config = self.find_by_route_name(session, route_name)

        if not config:
            return False

        config.enabled = 0
        session.commit()

        return True

    def enable_route(self, session: Session, route_name: str) -> bool:
        """
        Enable rate limit for a route.

        Args:
            session: Database session
            route_name: Route name

        Returns:
            True if enabled, False if not found
        """
        config = self.find_by_route_name(session, route_name)

        if not config:
            return False

        config.enabled = 1
        session.commit()

        return True

