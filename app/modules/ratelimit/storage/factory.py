"""
Storage factory for rate limiting.

Creates appropriate storage backend based on configuration.
"""

from app.modules.ratelimit.storage.base import RateLimitStorageProtocol
from app.modules.ratelimit.storage.memory import MemoryRateLimitStorage
from config import Config
from logger import get_logger

logger = get_logger(__name__)


def create_storage() -> RateLimitStorageProtocol:
    """
    Create rate limit storage based on configuration.

    Returns:
        Storage instance (Memory or Redis)
    """
    config = Config()
    storage_type = config.ratelimit.storage.lower()

    if storage_type == "redis":
        # Import Redis storage only when needed
        try:
            from app.modules.ratelimit.storage.redis import RedisRateLimitStorage

            # Get Redis configuration
            redis_config = config.ratelimit.redis

            storage = RedisRateLimitStorage(
                host=redis_config.host,
                port=redis_config.port,
                db=redis_config.db,
                password=redis_config.password if redis_config.password else None,
                key_prefix=redis_config.key_prefix,
                socket_timeout=redis_config.socket_timeout,
                socket_connect_timeout=redis_config.socket_connect_timeout,
                max_connections=redis_config.max_connections,
            )

            logger.info(
                "rate_limit_storage_created",
                storage_type="redis",
                host=redis_config.host,
                port=redis_config.port,
            )

            return storage

        except ImportError as e:
            logger.warning(
                "redis_import_failed",
                error=str(e),
                fallback="memory",
            )
            # Fall back to memory storage
            storage = MemoryRateLimitStorage()
            logger.info(
                "rate_limit_storage_created",
                storage_type="memory (fallback)",
            )
            return storage

        except Exception as e:
            logger.error(
                "redis_creation_failed",
                error=str(e),
                fallback="memory",
            )
            # Fall back to memory storage
            storage = MemoryRateLimitStorage()
            logger.info(
                "rate_limit_storage_created",
                storage_type="memory (fallback)",
            )
            return storage

    else:
        # Default to memory storage
        storage = MemoryRateLimitStorage()
        logger.info(
            "rate_limit_storage_created",
            storage_type="memory",
        )
        return storage

