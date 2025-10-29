"""
Shared Dependencies for FastAPI Application.

Provides dependency injection for configuration, storage, and services.
"""

import trace.codes as codes
from functools import lru_cache

from fastapi import Depends

from config import Config
from logger import get_logger
from storage_backend import create_storage
from storage_backend.base import StorageProtocol

logger = get_logger(__name__)


@lru_cache()
def get_config() -> Config:
    """
    Get configuration singleton.

    Cached to avoid reloading config on every request.

    Returns:
        Config: Application configuration
    """
    return Config()


def get_storage() -> StorageProtocol:
    """
    Dependency for getting storage backend.

    Creates storage instance based on configuration.
    Used for dependency injection in FastAPI endpoints.

    Yields:
        StorageProtocol: Storage backend instance

    Example:
        @app.post("/upload")
        async def upload(storage: StorageProtocol = Depends(get_storage)):
            storage.upload_file(...)
    """
    config = get_config()

    logger.debug(codes.STORAGE_DEPENDENCY_INJECTING, backend=config.storage.backend)

    storage = create_storage(config)

    try:
        yield storage
    finally:
        logger.debug(codes.STORAGE_DEPENDENCY_RELEASED)


def get_health_service(config: Config = Depends(get_config)):
    """
    Get health service instance.

    Service is stateless and lightweight.
    Dependencies are injected by FastAPI.

    Args:
        config: Application configuration (injected)

    Returns:
        HealthService: Health check service instance
    """
    from app.modules.health import HealthService

    return HealthService(config)


def get_upload_service(
    config: Config = Depends(get_config),
    storage: StorageProtocol = Depends(get_storage),
):
    """
    Get upload service instance.

    Service is stateless and lightweight.
    Dependencies are injected by FastAPI.

    Args:
        config: Application configuration (injected)
        storage: Storage backend (injected)

    Returns:
        UploadService: File upload service instance
    """
    from app.modules.upload import UploadService

    return UploadService(config, storage)


def get_file_service(
    config: Config = Depends(get_config),
    storage: StorageProtocol = Depends(get_storage),
):
    """
    Get file management service instance.

    Service uses database for metadata storage and queries.
    Dependencies are injected by FastAPI.

    Args:
        config: Application configuration (injected)
        storage: Storage backend (injected)

    Returns:
        FileManagementService: File management service instance
    """
    from app.modules.files import FileManagementService

    return FileManagementService(config, storage)
