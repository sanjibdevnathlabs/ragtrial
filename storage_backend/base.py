"""
Storage Backend Protocol.

Defines the interface that all storage implementations must follow.
Uses typing.Protocol for duck typing (no inheritance required).
"""

from typing import BinaryIO, Dict, List, Protocol


class StorageProtocol(Protocol):
    """Protocol defining storage backend interface.

    All storage implementations (local, S3, etc.) must implement these methods.
    Uses Protocol instead of ABC for duck typing and flexibility.
    """

    def upload_file(self, file_stream: BinaryIO, filename: str) -> str:
        """
        Upload file to storage.

        Args:
            file_stream: Binary file stream to upload
            filename: Target filename in storage

        Returns:
            Full path or key of uploaded file

        Raises:
            IOError: If upload fails
        """
        ...

    def download_file(self, filename: str) -> BinaryIO:
        """
        Download file from storage.

        Args:
            filename: Name of file to download

        Returns:
            Binary file stream

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If download fails
        """
        ...

    def delete_file(self, filename: str) -> bool:
        """
        Delete file from storage.

        Args:
            filename: Name of file to delete

        Returns:
            True if deleted successfully

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If deletion fails
        """
        ...

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in storage.

        Args:
            prefix: Optional prefix to filter files

        Returns:
            List of filenames matching prefix
        """
        ...

    def file_exists(self, filename: str) -> bool:
        """
        Check if file exists in storage.

        Args:
            filename: Name of file to check

        Returns:
            True if file exists
        """
        ...

    def get_file_metadata(self, filename: str) -> Dict[str, str]:
        """
        Get metadata for file.

        Args:
            filename: Name of file

        Returns:
            Dictionary with file metadata (size, modified_time, etc.)

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        ...
