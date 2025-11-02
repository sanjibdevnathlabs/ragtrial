"""
In-memory rate limit storage.

Uses Python dictionary with threading locks for thread-safe operations.
Suitable for single-instance deployments and development.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import DefaultDict, List


class MemoryRateLimitStorage:
    """
    In-memory rate limit storage using sliding window.

    Thread-safe implementation using locks.
    Stores timestamps of requests and counts within window.

    Note: Data is lost on application restart.
    Not suitable for distributed deployments.
    """

    def __init__(self):
        """Initialize in-memory storage."""
        self._data: DefaultDict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def increment(self, key: str, window_seconds: int) -> int:
        """
        Increment request count for key.

        Args:
            key: Unique identifier
            window_seconds: Time window in seconds

        Returns:
            Current count within window
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - window_seconds

            # Remove expired timestamps
            self._data[key] = [
                ts for ts in self._data[key] if ts > cutoff_time
            ]

            # Add current request
            self._data[key].append(current_time)

            return len(self._data[key])

    def get_count(self, key: str, window_seconds: int) -> int:
        """
        Get current request count.

        Args:
            key: Unique identifier
            window_seconds: Time window in seconds

        Returns:
            Count within window
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - window_seconds

            # Count timestamps within window
            self._data[key] = [
                ts for ts in self._data[key] if ts > cutoff_time
            ]

            return len(self._data[key])

    def reset(self, key: str) -> None:
        """
        Reset count for key.

        Args:
            key: Unique identifier
        """
        with self._lock:
            if key in self._data:
                del self._data[key]

    def cleanup(self) -> int:
        """
        Cleanup all expired entries.

        Returns:
            Number of keys removed
        """
        with self._lock:
            keys_to_remove = []
            current_time = time.time()

            for key, timestamps in self._data.items():
                # Remove timestamps older than 1 hour (conservative cleanup)
                cutoff = current_time - 3600
                self._data[key] = [ts for ts in timestamps if ts > cutoff]

                # Remove key if empty
                if not self._data[key]:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._data[key]

            return len(keys_to_remove)

    def get_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dict with total_keys and total_requests
        """
        with self._lock:
            return {
                "total_keys": len(self._data),
                "total_requests": sum(len(timestamps) for timestamps in self._data.values()),
            }

