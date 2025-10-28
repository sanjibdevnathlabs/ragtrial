"""
File service with business logic.

Coordinates between file repository and external systems.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional

from app.modules.file.entity import File
from app.modules.file.repository import FileRepository
from database.exceptions import DatabaseQueryError
from database.session import SessionFactory
from logger import get_logger
import trace.codes as codes
import constants

logger = get_logger(__name__)


class FileService:
    """
    File service for business logic.
    
    Handles:
    - File record creation with UUID and checksum
    - Duplicate detection
    - File listing and retrieval
    - Soft delete
    - Indexing status management
    """

    def __init__(self):
        """Initialize file service."""
        self.repository = FileRepository()
        self.session_factory = SessionFactory()

    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """
        Calculate SHA-256 checksum of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest checksum
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()

    def check_duplicate(self, checksum: str) -> Optional[Dict]:
        """
        Check if file with checksum already exists.
        
        Args:
            checksum: SHA-256 checksum
            
        Returns:
            File dict if duplicate exists, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            existing = self.repository.find_by_checksum(session, checksum)
            return existing.to_dict() if existing else None

    def create_file_record(
        self,
        filename: str,
        file_path: str,
        file_size: int,
        checksum: str,
        storage_backend: str = "local"
    ) -> Dict:
        """
        Create file metadata record.
        
        Args:
            filename: Original filename
            file_path: Path where file is stored (UUID-based)
            file_size: File size in bytes
            checksum: SHA-256 checksum
            storage_backend: Storage backend identifier
            
        Returns:
            Created file as dictionary
            
        Raises:
            DatabaseQueryError: If creation fails
        """
        logger.info(
            codes.DB_REPOSITORY_STARTED,
            operation="create_file_record",
            filename=filename
        )

        try:
            # Generate UUID for file ID
            file_id = File.generate_id()
            
            # Extract file type (without dot)
            file_type = File.get_file_type_from_filename(filename)
            
            # Create file entity
            file = File(
                id=file_id,
                filename=filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                checksum=checksum,
                storage_backend=storage_backend,
                indexed=False
            )

            # Save to database
            with self.session_factory.get_write_session() as session:
                created_file = self.repository.create(session, file)
                
                logger.info(
                    codes.DB_REPOSITORY_COMPLETED,
                    operation="create_file_record",
                    file_id=created_file.id,
                    msg=constants.MSG_DB_ENTITY_CREATED
                )
                
                return created_file.to_dict()

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="create_file_record",
                error=str(e),
                exc_info=True
            )
            raise

    def get_file_by_id(self, file_id: str) -> Optional[Dict]:
        """
        Get file by ID.
        
        Args:
            file_id: File ID
            
        Returns:
            File dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            file = self.repository.find_by_id(session, file_id)
            return file.to_dict() if file else None

    def get_file_by_filename(self, filename: str) -> Optional[Dict]:
        """
        Get file by filename.
        
        Args:
            filename: Filename to search for
            
        Returns:
            File dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            file = self.repository.find_by_filename(session, filename)
            return file.to_dict() if file else None

    def list_all_files(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict]:
        """
        List all active files.
        
        Args:
            limit: Maximum number of files
            offset: Number of files to skip
            
        Returns:
            List of file dictionaries
        """
        with self.session_factory.get_read_session() as session:
            files = self.repository.find_all(
                session,
                include_deleted=False,
                limit=limit,
                offset=offset,
                order_by="created_at",
                order_desc=True
            )
            return [f.to_dict() for f in files]

    def delete_file(self, file_id: str) -> bool:
        """
        Soft delete file by ID.
        
        Args:
            file_id: File ID
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(
            codes.DB_REPOSITORY_STARTED,
            operation="delete_file",
            file_id=file_id
        )

        with self.session_factory.get_write_session() as session:
            deleted = self.repository.delete(session, file_id)
            
            if deleted:
                logger.info(
                    codes.DB_REPOSITORY_COMPLETED,
                    operation="delete_file",
                    file_id=file_id,
                    msg=constants.MSG_DB_ENTITY_DELETED
                )
            
            return deleted

    def mark_as_indexed(self, file_id: str) -> bool:
        """
        Mark file as indexed in vector store.
        
        Args:
            file_id: File ID
            
        Returns:
            True if marked, False if not found
        """
        with self.session_factory.get_write_session() as session:
            return self.repository.mark_as_indexed(session, file_id)

    def get_unindexed_files(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get files that haven't been indexed yet.
        
        Args:
            limit: Maximum number of files
            
        Returns:
            List of file dictionaries
        """
        with self.session_factory.get_read_session() as session:
            files = self.repository.find_unindexed_files(session, limit=limit)
            return [f.to_dict() for f in files]

    def get_indexed_files(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get files that have been indexed.
        
        Args:
            limit: Maximum number of files
            
        Returns:
            List of file dictionaries
        """
        with self.session_factory.get_read_session() as session:
            files = self.repository.find_indexed_files(session, limit=limit)
            return [f.to_dict() for f in files]

    def get_total_size(self) -> int:
        """
        Get total size of all files in bytes.
        
        Returns:
            Total size in bytes
        """
        with self.session_factory.get_read_session() as session:
            return self.repository.get_total_size(session)

    def get_statistics(self) -> Dict:
        """
        Get file statistics.
        
        Returns:
            Dictionary with counts and sizes
        """
        with self.session_factory.get_read_session() as session:
            total_count = self.repository.count(session, include_deleted=False)
            indexed_count = len(self.repository.find_indexed_files(session))
            total_size = self.repository.get_total_size(session)
            
            return {
                "total_files": total_count,
                "indexed_files": indexed_count,
                "unindexed_files": total_count - indexed_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }

