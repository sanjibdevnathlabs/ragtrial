"""
Local File System Storage Implementation.

Stores documents in local file system directory.
"""

import shutil
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Dict, List

import constants
from logger import get_logger
from trace import codes

logger = get_logger(__name__)


class LocalStorage:
    """Local file system storage implementation.
    
    Stores files in configured local directory.
    Thread-safe for concurrent operations.
    """

    def __init__(self, config):
        """
        Initialize local storage.
        
        Args:
            config: Application configuration
        """
        logger.info(
            codes.STORAGE_INITIALIZING,
            backend=constants.STORAGE_BACKEND_LOCAL
        )
        
        self.storage_path = Path(config.storage.local.path)
        self._ensure_directory_exists()
        
        logger.info(
            codes.STORAGE_INITIALIZED,
            backend=constants.STORAGE_BACKEND_LOCAL,
            path=str(self.storage_path),
            message=codes.MSG_STORAGE_INITIALIZED
        )

    def _ensure_directory_exists(self) -> None:
        """Create storage directory if it doesn't exist."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file_stream: BinaryIO, filename: str) -> str:
        """
        Upload file to local storage.
        
        Args:
            file_stream: Binary file stream or bytes
            filename: Target filename
            
        Returns:
            Full path to uploaded file
        """
        file_path = self.storage_path / filename
        
        logger.info(
            codes.STORAGE_UPLOADING,
            filename=filename,
            backend=constants.STORAGE_BACKEND_LOCAL
        )
        
        # Handle both bytes and file stream
        if isinstance(file_stream, bytes):
            file_path.write_bytes(file_stream)
        else:
            file_path.write_bytes(file_stream.read())
        
        logger.info(
            codes.STORAGE_UPLOADED,
            filename=filename,
            path=str(file_path),
            message=codes.MSG_STORAGE_UPLOADED
        )
        
        return str(file_path)

    def download_file(self, filename: str) -> BinaryIO:
        """
        Download file from local storage.
        
        Args:
            filename: Name of file to download
            
        Returns:
            Binary file stream
        """
        file_path = self.storage_path / filename
        
        if not file_path.exists():
            logger.error(
                codes.STORAGE_FILE_NOT_FOUND,
                filename=filename
            )
            raise FileNotFoundError(
                f"{constants.ERROR_FILE_NOT_FOUND_STORAGE}: {filename}"
            )
        
        logger.info(
            codes.STORAGE_DOWNLOADING,
            filename=filename
        )
        
        content = file_path.read_bytes()
        stream = BytesIO(content)
        
        logger.info(
            codes.STORAGE_DOWNLOADED,
            filename=filename,
            size=len(content)
        )
        
        return stream

    def delete_file(self, filename: str) -> bool:
        """
        Delete file from local storage.
        
        Args:
            filename: Name of file to delete
            
        Returns:
            True if deleted successfully
        """
        file_path = self.storage_path / filename
        
        if not file_path.exists():
            logger.warning(
                codes.STORAGE_FILE_NOT_FOUND,
                filename=filename
            )
            return False
        
        logger.info(
            codes.STORAGE_DELETING,
            filename=filename
        )
        
        file_path.unlink()
        
        logger.info(
            codes.STORAGE_DELETED,
            filename=filename,
            message=codes.MSG_STORAGE_DELETED
        )
        
        return True

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in local storage.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of filenames
        """
        logger.info(
            codes.STORAGE_LISTING,
            prefix=prefix or "all"
        )
        
        pattern = f"{prefix}*" if prefix else "*"
        files = [f.name for f in self.storage_path.glob(pattern) if f.is_file()]
        
        logger.info(
            codes.STORAGE_LISTED,
            count=len(files)
        )
        
        return sorted(files)

    def file_exists(self, filename: str) -> bool:
        """
        Check if file exists.
        
        Args:
            filename: Name of file to check
            
        Returns:
            True if file exists
        """
        exists = (self.storage_path / filename).exists()
        
        if exists:
            logger.debug(
                codes.STORAGE_FILE_EXISTS,
                filename=filename
            )
        
        return exists

    def get_file_metadata(self, filename: str) -> Dict[str, str]:
        """
        Get file metadata.
        
        Args:
            filename: Name of file
            
        Returns:
            Dictionary with metadata
        """
        file_path = self.storage_path / filename
        
        if not file_path.exists():
            logger.error(
                codes.STORAGE_FILE_NOT_FOUND,
                filename=filename
            )
            raise FileNotFoundError(
                f"{constants.ERROR_FILE_NOT_FOUND_STORAGE}: {filename}"
            )
        
        stat = file_path.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        return {
            "filename": filename,
            "size": str(stat.st_size),
            "modified_time": modified_time.isoformat(),
            "path": str(file_path)
        }

