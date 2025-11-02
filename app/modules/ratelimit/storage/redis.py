"""
Redis-based rate limit storage using sorted sets.

Implements distributed rate limiting with Redis for multi-server deployments.
"""

import time
from typing import Dict, Optional

import redis

from app.modules.ratelimit.storage.base import RateLimitStorageProtocol
from logger import get_logger

logger = get_logger(__name__)


class RedisRateLimitStorage(RateLimitStorageProtocol):
    """
    Redis-based rate limit storage using sorted sets.

    Uses Redis ZSET for sliding window implementation:
    - Score: timestamp (milliseconds)
    - Member: unique request ID (timestamp + random)

    Advantages:
    - Distributed: Works across multiple servers
    - Persistent: Survives application restarts
    - Atomic: All operations are atomic via Lua scripts
    - Accurate: True sliding window algorithm
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "ratelimit",
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        max_connections: int = 50,
    ):
        """
        Initialize Redis storage.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (None for no auth)
            key_prefix: Prefix for all rate limit keys
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
            max_connections: Maximum connections in pool
        """
        self.key_prefix = key_prefix

        # Create connection pool
        pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password if password else None,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            max_connections=max_connections,
            decode_responses=True,  # Decode bytes to strings
        )

        # Create Redis client
        self.redis = redis.Redis(connection_pool=pool)

        # Test connection
        try:
            self.redis.ping()
            logger.info(
                "redis_connected",
                host=host,
                port=port,
                db=db,
            )
        except redis.ConnectionError as e:
            logger.error(
                "redis_connection_failed",
                host=host,
                port=port,
                error=str(e),
            )
            raise

    def _make_key(self, key: str) -> str:
        """
        Build Redis key with prefix.

        Args:
            key: Rate limit key

        Returns:
            Prefixed Redis key
        """
        return f"{self.key_prefix}:{key}"

    def increment(self, key: str, window_seconds: int) -> int:
        """
        Increment request count for key using sliding window.

        Uses Lua script for atomic operation:
        1. Remove expired entries
        2. Count current entries
        3. Add new entry
        4. Set key expiration

        Args:
            key: Rate limit key
            window_seconds: Time window in seconds

        Returns:
            Current request count in window
        """
        redis_key = self._make_key(key)
        now_ms = int(time.time() * 1000)
        window_start_ms = now_ms - (window_seconds * 1000)

        # Lua script for atomic sliding window operation
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local window_seconds = tonumber(ARGV[3])
        
        -- Remove expired entries
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
        
        -- Count current entries
        local count = redis.call('ZCARD', key)
        
        -- Add new entry (timestamp as both score and member for uniqueness)
        redis.call('ZADD', key, now, now)
        
        -- Set expiration (window + buffer for cleanup)
        redis.call('EXPIRE', key, window_seconds + 60)
        
        -- Return count + 1 (including new entry)
        return count + 1
        """

        try:
            count = self.redis.eval(
                lua_script,
                1,  # Number of keys
                redis_key,  # KEYS[1]
                now_ms,  # ARGV[1]
                window_start_ms,  # ARGV[2]
                window_seconds,  # ARGV[3]
            )
            return int(count)

        except redis.RedisError as e:
            logger.error(
                "redis_increment_failed",
                key=redis_key,
                error=str(e),
            )
            # Fail open: allow request on Redis error
            return 0

    def get_count(self, key: str, window_seconds: int) -> int:
        """
        Get current request count in window.

        Args:
            key: Rate limit key
            window_seconds: Time window in seconds

        Returns:
            Current request count
        """
        redis_key = self._make_key(key)
        now_ms = int(time.time() * 1000)
        window_start_ms = now_ms - (window_seconds * 1000)

        try:
            # Count entries in current window
            count = self.redis.zcount(redis_key, window_start_ms, now_ms)
            return count

        except redis.RedisError as e:
            logger.error(
                "redis_get_count_failed",
                key=redis_key,
                error=str(e),
            )
            return 0

    def reset(self, key: str) -> None:
        """
        Reset rate limit for key.

        Args:
            key: Rate limit key
        """
        redis_key = self._make_key(key)

        try:
            self.redis.delete(redis_key)
            logger.info(
                "redis_key_reset",
                key=redis_key,
            )

        except redis.RedisError as e:
            logger.error(
                "redis_reset_failed",
                key=redis_key,
                error=str(e),
            )

    def cleanup(self) -> int:
        """
        Cleanup expired entries (Redis handles via EXPIRE, no-op here).

        Returns:
            Always returns 0 (Redis auto-expires keys)
        """
        # Redis automatically removes expired keys via EXPIRE command
        # No manual cleanup needed
        return 0

    def get_stats(self) -> Dict[str, int]:
        """
        Get storage statistics.

        Returns:
            Dict with stats: active_keys, total_requests
        """
        try:
            # Scan for all rate limit keys
            pattern = f"{self.key_prefix}:*"
            keys = list(self.redis.scan_iter(match=pattern, count=100))

            active_keys = len(keys)

            # Count total requests across all keys
            total_requests = 0
            for key in keys:
                try:
                    count = self.redis.zcard(key)
                    total_requests += count
                except redis.RedisError:
                    continue

            return {
                "active_keys": active_keys,
                "total_requests": total_requests,
            }

        except redis.RedisError as e:
            logger.error(
                "redis_stats_failed",
                error=str(e),
            )
            return {
                "active_keys": 0,
                "total_requests": 0,
            }

    def close(self) -> None:
        """Close Redis connection."""
        try:
            self.redis.close()
            logger.info("redis_connection_closed")
        except Exception as e:
            logger.error(
                "redis_close_failed",
                error=str(e),
            )

