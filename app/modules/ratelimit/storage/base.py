"""
Rate limit storage protocol.

Defines interface for rate limit storage backends.
"""

from typing import Protocol


class RateLimitStorageProtocol(Protocol):
    """
    Protocol for rate limit storage backends.

    Implementations must provide methods for tracking request counts
    within sliding time windows.
    """

    def increment(self, key: str, window_seconds: int) -> int:
        """
        Increment request count for key within window.

        Args:
            key: Unique identifier (e.g., "route_name:ip_address")
            window_seconds: Time window in seconds

        Returns:
            Current request count within window
        """
        ...

    def get_count(self, key: str, window_seconds: int) -> int:
        """
        Get current request count for key within window.

        Args:
            key: Unique identifier
            window_seconds: Time window in seconds

        Returns:
            Request count within window
        """
        ...

    def reset(self, key: str) -> None:
        """
        Reset request count for key.

        Args:
            key: Unique identifier
        """
        ...

    def cleanup(self) -> int:
        """
        Cleanup expired entries.

        Returns:
            Number of entries removed
        """
        ...

