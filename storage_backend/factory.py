"""
Storage Backend Factory.

Creates appropriate storage backend based on configuration.
Follows Factory pattern for dynamic backend selection.
"""

from typing import Dict, Type

import constants
from logger import get_logger
from storage_backend.base import StorageProtocol
from storage_backend.implementations.local import LocalStorage
from storage_backend.implementations.s3 import S3Storage
from trace import codes

logger = get_logger(__name__)


# Strategy map: backend name -> implementation class
_STORAGE_MAP: Dict[str, Type[StorageProtocol]] = {
    constants.STORAGE_BACKEND_LOCAL: LocalStorage,
    constants.STORAGE_BACKEND_S3: S3Storage,
}


def create_storage(config) -> StorageProtocol:
    """
    Create storage backend based on configuration.
    
    Factory method that instantiates the appropriate storage
    implementation based on config.storage.backend setting.
    
    Args:
        config: Application configuration
        
    Returns:
        Storage backend instance implementing StorageProtocol
        
    Raises:
        ValueError: If backend is not supported
        
    Example:
        >>> storage = create_storage(config)
        >>> storage.upload_file(file_stream, "document.pdf")
    """
    backend = config.storage.backend
    
    if backend not in _STORAGE_MAP:
        logger.error(
            codes.STORAGE_ERROR,
            backend=backend,
            supported=list(_STORAGE_MAP.keys()),
            message=constants.ERROR_INVALID_STORAGE_BACKEND
        )
        raise ValueError(
            f"{constants.ERROR_INVALID_STORAGE_BACKEND}: {backend}. "
            f"Supported: {list(_STORAGE_MAP.keys())}"
        )
    
    storage_class = _STORAGE_MAP[backend]
    
    logger.info(
        "storage_factory_creating",
        backend=backend,
        class_name=storage_class.__name__
    )
    
    return storage_class(config)


def get_supported_backends() -> list:
    """
    Get list of supported storage backends.
    
    Returns:
        List of backend names
    """
    return list(_STORAGE_MAP.keys())

