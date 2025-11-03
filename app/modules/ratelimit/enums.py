"""
Rate limit enums.

Defines enumerations for rate limiting behavior.
"""

from enum import Enum


class RateLimitKeyStrategy(str, Enum):
    """
    Strategy for building rate limit keys.

    Determines how to uniquely identify clients for rate limiting.
    """

    IP = "ip"
    """Rate limit per IP address (default for public endpoints)."""

    USER = "user"
    """Rate limit per authenticated user ID."""

    SESSION = "session"
    """Rate limit per session ID (from cookies/headers)."""

    ROUTE = "route"
    """Rate limit per route name only (global route limit)."""

    IP_AND_ROUTE = "ip_and_route"
    """Rate limit per IP + route combination."""

    USER_AND_ROUTE = "user_and_route"
    """Rate limit per user + route combination."""

