"""
File management service.

Handles file listing, metadata, and deletion operations.
"""

from app.api.models import FileListResponse, FileMetadataResponse
from utils.singleton import SingletonMeta
from config import Config
from storage_backend.base import StorageProtocol
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)


class FileService(metaclass=SingletonMeta):
    """
    Singleton service for file management operations.
    
    Thread-safe singleton ensures only one instance exists.
    Optimized for high RPS scenarios.
    """
    
    def __init__(self, config: Config, storage: StorageProtocol):
        """
        Initialize file service.
        
        Only called once - subsequent calls return existing instance.
        
        Args:
            config: Application configuration
            storage: Storage backend instance
        """
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self.config = config
            self.storage = storage
            self._initialized = True
    
    def list_files(self) -> FileListResponse:
        """
        List all files in storage.
        
        Returns:
            FileListResponse: List of files with count
            
        Raises:
            Exception: If listing fails
        """
        logger.debug(codes.STORAGE_LISTING)
        
        files = self.storage.list_files()
        
        logger.info(
            codes.API_FILES_LISTED,
            count=len(files),
            backend=self.config.storage.backend
        )
        
        return FileListResponse(
            files=files,
            count=len(files),
            backend=self.config.storage.backend
        )
    
    def get_file_metadata(self, filename: str) -> FileMetadataResponse:
        """
        Get metadata for a file.
        
        Args:
            filename: Name of file
            
        Returns:
            FileMetadataResponse: File metadata
            
        Raises:
            FileNotFoundError: If file does not exist
            Exception: If metadata retrieval fails
        """
        logger.debug(codes.API_FILE_METADATA_RETRIEVED, filename=filename)
        
        if not self.storage.file_exists(filename):
            logger.warning(codes.API_FILE_NOT_FOUND, filename=filename)
            raise FileNotFoundError(codes.MSG_API_FILE_NOT_FOUND)
        
        metadata = self._get_metadata(filename)
        
        logger.info(codes.API_FILE_METADATA_RETRIEVED, filename=filename)
        
        return FileMetadataResponse(
            filename=metadata.get("filename", filename),
            size=str(metadata.get("size", 0)),
            modified_time=metadata.get("modified_time", ""),
            path=metadata.get("path"),
            etag=metadata.get("etag")
        )
    
    def delete_file(self, filename: str) -> dict:
        """
        Delete a file from storage.
        
        Args:
            filename: Name of file to delete
            
        Returns:
            dict: Success message with filename
            
        Raises:
            FileNotFoundError: If file does not exist
            Exception: If deletion fails
        """
        logger.info(codes.API_FILE_DELETED, filename=filename)
        
        if not self.storage.file_exists(filename):
            logger.warning(codes.API_FILE_NOT_FOUND, filename=filename)
            raise FileNotFoundError(codes.MSG_API_FILE_NOT_FOUND)
        
        self.storage.delete_file(filename)
        
        logger.info(codes.API_FILE_DELETED, filename=filename)
        
        return {
            "success": True,
            "message": codes.MSG_API_FILE_DELETED,
            "filename": filename
        }
    
    def _get_metadata(self, filename: str) -> dict:
        """
        Get metadata from storage.
        
        Args:
            filename: Name of file
            
        Returns:
            dict: File metadata
            
        Raises:
            Exception: If metadata retrieval fails
        """
        try:
            return self.storage.get_file_metadata(filename)
        except Exception as e:
            logger.error(
                codes.API_ERROR,
                operation="get_metadata",
                filename=filename,
                error=str(e),
                exc_info=True
            )
            raise

