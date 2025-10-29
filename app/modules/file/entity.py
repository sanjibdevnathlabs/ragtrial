"""
File entity model.

Represents file metadata stored in database.
"""

import uuid
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, String

import constants
from database.base_model import BaseModel


class File(BaseModel):
    """
    File metadata entity.

    Fields:
        id: UUID primary key
        filename: Original filename
        file_path: Path to stored file (uses UUID-based name)
        file_type: File extension without dot (pdf, txt, md)
        file_size: File size in bytes
        checksum: SHA-256 checksum for duplicate detection
        storage_backend: Storage backend identifier (local, s3)
        indexed: Whether file content is indexed in vector store
        indexed_at: Timestamp when indexed (milliseconds)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)
    """

    __tablename__ = constants.DB_TABLE_FILES

    # Override table name from base model
    __table_args__ = {"extend_existing": True}

    # File-specific fields
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)
    storage_backend = Column(String(50), nullable=False)
    indexed = Column(Boolean, nullable=False, default=False)
    indexed_at = Column(BigInteger, nullable=True)

    @staticmethod
    def generate_id() -> str:
        """
        Generate a new UUID for file ID.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    @staticmethod
    def get_file_type_from_filename(filename: str) -> str:
        """
        Extract file type from filename (without dot).

        Args:
            filename: Original filename with extension

        Returns:
            File type without dot (e.g., 'pdf', 'txt')
        """
        if "." in filename:
            extension = filename.rsplit(".", 1)[1].lower()
            return extension
        return "unknown"

    def mark_as_indexed(self) -> None:
        """
        Mark file as indexed in vector store.

        Updates indexed flag and sets indexed_at timestamp.
        """
        self.indexed = True
        self.indexed_at = self._get_current_timestamp()
        self.update_timestamp()

    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """
        Convert to dictionary with additional computed fields.

        Args:
            exclude: Fields to exclude

        Returns:
            Dictionary representation
        """
        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["is_indexed"] = self.indexed
        data["is_deleted"] = self.is_deleted()

        return data

    def __repr__(self) -> str:
        """String representation."""
        deleted = " (DELETED)" if self.is_deleted() else ""
        indexed = " (INDEXED)" if self.indexed else ""
        return f"<File(id={self.id!r}, filename={self.filename!r}){deleted}{indexed}>"
