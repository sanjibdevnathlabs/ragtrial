"""
Rate limit configuration entity.

Stores runtime-configurable rate limits in database.
"""

from sqlalchemy import BigInteger, Column, Integer, String, Text, text

import constants
from database.base_model import BaseModel


class RateLimitConfig(BaseModel):
    """
    Rate limit configuration model.

    Stores per-route rate limits in database for runtime configuration.
    Use route_name='global' for global default that applies to all routes.
    """

    __tablename__ = constants.DB_TABLE_RATE_LIMIT_CONFIGS

    route_name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Route name (use 'global' for global default)",
    )

    requests = Column(
        Integer,
        nullable=False,
        comment="Number of requests allowed",
    )

    window_seconds = Column(
        Integer,
        nullable=False,
        comment="Time window in seconds",
    )

    enabled = Column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        index=True,
        comment="Enable/disable this limit (1=enabled, 0=disabled)",
    )

    key_strategy = Column(
        String(50),
        nullable=False,
        default="ip",
        server_default=text("'ip'"),
        comment="Rate limit key strategy: ip, user, session, route, ip_and_route, user_and_route",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description",
    )

    def to_dict(self) -> dict:
        """Convert entity to dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "route_name": self.route_name,
                "requests": self.requests,
                "window_seconds": self.window_seconds,
                "enabled": bool(self.enabled),
                "key_strategy": self.key_strategy,
                "description": self.description,
            }
        )
        return base_dict

    def is_enabled(self) -> bool:
        """Check if rate limit is enabled."""
        return bool(self.enabled)

    def is_global(self) -> bool:
        """Check if this is the global default."""
        return self.route_name == "global"

