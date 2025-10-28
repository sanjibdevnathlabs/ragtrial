"""
File management service.

Handles file listing, metadata, and deletion operations using database.
"""

from app.modules.files.response import FileListResponse, FileMetadataResponse
from app.modules.file.core import FileService as DBFileService
from utils.singleton import SingletonMeta
from config import Config
from storage_backend.base import StorageProtocol
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)


class FileManagementService(metaclass=SingletonMeta):
    """
    Singleton service for file management operations.
    
    Uses database for metadata storage and queries.
    Thread-safe singleton ensures only one instance exists.
    Optimized for high RPS scenarios.
    """
    
    def __init__(self, config: Config, storage: StorageProtocol):
        """
        Initialize file management service.
        
        Only called once - subsequent calls return existing instance.
        
        Args:
            config: Application configuration
            storage: Storage backend instance
        """
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self.config = config
            self.storage = storage
            self.db_file_service = DBFileService()
            self._initialized = True
    
    def list_files(self) -> FileListResponse:
        """
        List all files from database.
        
        Returns:
            FileListResponse: List of files with metadata
            
        Raises:
            Exception: If listing fails
        """
        logger.debug(codes.API_FILES_LISTED)
        
        files = self.db_file_service.list_all_files()
        
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
        Get metadata for a file from database.
        
        Args:
            filename: Original filename
            
        Returns:
            FileMetadataResponse: File metadata
            
        Raises:
            FileNotFoundError: If file does not exist
            Exception: If metadata retrieval fails
        """
        logger.debug(codes.API_FILE_METADATA_RETRIEVED, filename=filename)
        
        file_data = self.db_file_service.get_file_by_filename(filename)
        
        if not file_data:
            logger.warning(codes.API_FILE_NOT_FOUND, filename=filename)
            raise FileNotFoundError(codes.MSG_API_FILE_NOT_FOUND)
        
        logger.info(codes.API_FILE_METADATA_RETRIEVED, filename=filename)
        
        # Map database field names to API response field names
        file_data['file_id'] = file_data.pop('id')
        
        return FileMetadataResponse(**file_data)
    
    def delete_file(self, filename: str) -> dict:
        """
        Soft delete a file (database and storage).
        
        Args:
            filename: Original filename to delete
            
        Returns:
            dict: Success message with filename
            
        Raises:
            FileNotFoundError: If file does not exist
            Exception: If deletion fails
        """
        logger.info(codes.API_FILE_DELETED, filename=filename)
        
        # Get file from database
        file_data = self.db_file_service.get_file_by_filename(filename)
        
        if not file_data:
            logger.warning(codes.API_FILE_NOT_FOUND, filename=filename)
            raise FileNotFoundError(codes.MSG_API_FILE_NOT_FOUND)
        
        # Soft delete in database
        file_id = file_data["id"]
        self.db_file_service.delete_file(file_id)
        
        # Delete from storage backend
        file_path = file_data["file_path"]
        if self.storage.file_exists(file_path):
            self.storage.delete_file(file_path)
        
        logger.info(codes.API_FILE_DELETED, filename=filename)
        
        return {
            "success": True,
            "message": codes.MSG_API_FILE_DELETED,
            "filename": filename
        }

