"""
Upload service.

Handles file upload operations.
"""

from app.api.models import UploadResponse
from app.modules.upload.validators import UploadValidator
from utils.singleton import SingletonMeta
from config import Config
from storage_backend.base import StorageProtocol
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)


class UploadService(metaclass=SingletonMeta):
    """
    Singleton service for file upload operations.
    
    Thread-safe singleton ensures only one instance exists.
    Optimized for high RPS scenarios.
    """
    
    def __init__(self, config: Config, storage: StorageProtocol):
        """
        Initialize upload service.
        
        Only called once - subsequent calls return existing instance.
        
        Args:
            config: Application configuration
            storage: Storage backend instance
        """
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self.config = config
            self.storage = storage
            self.validator = UploadValidator(config)
            self._initialized = True
    
    def upload_file(self, filename: str, content: bytes) -> UploadResponse:
        """
        Upload file to storage.
        
        Args:
            filename: Name of file
            content: File content bytes
            
        Returns:
            UploadResponse: Upload result with metadata
            
        Raises:
            ValueError: If validation fails
            Exception: If upload fails
        """
        logger.info(codes.API_UPLOAD_STARTED, filename=filename)
        
        self._validate_file(filename, content)
        file_path = self._store_file(filename, content)
        
        logger.info(
            codes.API_UPLOAD_COMPLETED,
            filename=filename,
            path=file_path,
            size_bytes=len(content),
            backend=self.config.storage.backend
        )
        
        return UploadResponse(
            success=True,
            filename=filename,
            path=file_path,
            size=len(content),
            backend=self.config.storage.backend
        )
    
    def _validate_file(self, filename: str, content: bytes) -> None:
        """
        Validate file before upload.
        
        Args:
            filename: Name of file
            content: File content bytes
            
        Raises:
            ValueError: If validation fails
        """
        self.validator.validate_filename(filename)
        self.validator.validate_extension(filename)
        self.validator.validate_size(content, filename)
    
    def _store_file(self, filename: str, content: bytes) -> str:
        """
        Store file in storage backend.
        
        Args:
            filename: Name of file
            content: File content bytes
            
        Returns:
            str: File path in storage
            
        Raises:
            Exception: If storage fails
        """
        try:
            return self.storage.upload_file(filename, content)
        except Exception as e:
            logger.error(
                codes.API_UPLOAD_FAILED,
                filename=filename,
                error=str(e),
                exc_info=True
            )
            raise

