"""
File repository with custom query methods.

Extends BaseRepository with file-specific operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.file.entity import File
from database.base_repository import BaseRepository
from database.exceptions import DatabaseQueryError
from logger import get_logger
import trace.codes as codes
import constants

logger = get_logger(__name__)


class FileRepository(BaseRepository[File]):
    """
    Repository for file metadata operations.
    
    Extends BaseRepository with file-specific queries:
    - find_by_filename()
    - find_by_checksum()
    - find_unindexed_files()
    - find_indexed_files()
    - mark_as_indexed()
    - get_total_size()
    """

    def __init__(self):
        """Initialize file repository."""
        super().__init__(File)

    def find_by_filename(
        self,
        session: Session,
        filename: str,
        include_deleted: bool = False
    ) -> Optional[File]:
        """
        Find file by filename.
        
        Args:
            session: Database session
            filename: Filename to search for
            include_deleted: Include soft-deleted files
            
        Returns:
            File if found, None otherwise
        """
        return self.find_by_field(session, "filename", filename, include_deleted)

    def find_by_checksum(
        self,
        session: Session,
        checksum: str,
        include_deleted: bool = False
    ) -> Optional[File]:
        """
        Find file by checksum (duplicate detection).
        
        Args:
            session: Database session
            checksum: SHA-256 checksum
            include_deleted: Include soft-deleted files
            
        Returns:
            File if found (duplicate exists), None otherwise
        """
        return self.find_by_field(session, "checksum", checksum, include_deleted)

    def find_unindexed_files(
        self,
        session: Session,
        limit: Optional[int] = None
    ) -> List[File]:
        """
        Find files that haven't been indexed yet.
        
        Args:
            session: Database session
            limit: Maximum number of files to return
            
        Returns:
            List of unindexed files
        """
        return self.find_by_fields(
            session,
            filters={"indexed": False},
            include_deleted=False
        )[:limit] if limit else self.find_by_fields(
            session,
            filters={"indexed": False},
            include_deleted=False
        )

    def find_indexed_files(
        self,
        session: Session,
        limit: Optional[int] = None
    ) -> List[File]:
        """
        Find files that have been indexed.
        
        Args:
            session: Database session
            limit: Maximum number of files to return
            
        Returns:
            List of indexed files
        """
        return self.find_by_fields(
            session,
            filters={"indexed": True},
            include_deleted=False
        )[:limit] if limit else self.find_by_fields(
            session,
            filters={"indexed": True},
            include_deleted=False
        )

    def mark_as_indexed(
        self,
        session: Session,
        file_id: str
    ) -> bool:
        """
        Mark file as indexed.
        
        Args:
            session: Database session
            file_id: File ID
            
        Returns:
            True if marked, False if not found
            
        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="mark_as_indexed",
                file_id=file_id
            )

            file = self.find_by_id(session, file_id)
            if file is None:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    file_id=file_id
                )
                return False

            file.mark_as_indexed()
            self.update(session, file)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="mark_as_indexed",
                file_id=file_id
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="mark_as_indexed",
                error=str(e),
                exc_info=True
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="mark_as_indexed",
                details={"file_id": file_id},
                original_error=e
            ) from e

    def get_total_size(
        self,
        session: Session,
        include_deleted: bool = False
    ) -> int:
        """
        Get total size of all files in bytes.
        
        Args:
            session: Database session
            include_deleted: Include soft-deleted files
            
        Returns:
            Total size in bytes
        """
        try:
            from sqlalchemy import func

            query = session.query(func.sum(File.file_size))

            if not include_deleted:
                query = query.filter(File.deleted_at.is_(None))

            result = query.scalar()
            return result or 0

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="get_total_size",
                error=str(e),
                exc_info=True
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="get_total_size",
                original_error=e
            ) from e

    def find_by_storage_backend(
        self,
        session: Session,
        storage_backend: str,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Find files by storage backend.
        
        Args:
            session: Database session
            storage_backend: Storage backend identifier (local, s3)
            include_deleted: Include soft-deleted files
            
        Returns:
            List of files
        """
        return self.find_by_fields(
            session,
            filters={"storage_backend": storage_backend},
            include_deleted=include_deleted
        )

    def find_by_file_type(
        self,
        session: Session,
        file_type: str,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Find files by file type.
        
        Args:
            session: Database session
            file_type: File extension without dot (pdf, txt, etc.)
            include_deleted: Include soft-deleted files
            
        Returns:
            List of files
        """
        return self.find_by_fields(
            session,
            filters={"file_type": file_type},
            include_deleted=include_deleted
        )

