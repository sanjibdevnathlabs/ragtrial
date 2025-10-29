"""
Upload validation logic.

Validates file upload requests.
"""

import trace.codes as codes
from pathlib import Path

from config import Config
from logger import get_logger

logger = get_logger(__name__)

BYTES_PER_MB = 1048576


class UploadValidator:
    """Validator for file uploads."""

    def __init__(self, config: Config):
        """
        Initialize validator.

        Args:
            config: Application configuration
        """
        self.config = config

    def validate_filename(self, filename: str) -> None:
        """
        Validate filename is not empty.

        Args:
            filename: Name of file

        Raises:
            ValueError: If filename is missing
        """
        if not filename:
            logger.warning(codes.API_VALIDATION_ERROR, error="missing_filename")
            raise ValueError("Filename is required")

    def validate_extension(self, filename: str) -> None:
        """
        Validate file extension is allowed.

        Args:
            filename: Name of file

        Raises:
            ValueError: If extension not allowed
        """
        file_ext = Path(filename).suffix.lower()

        if file_ext not in self.config.storage.allowed_extensions:
            logger.warning(
                codes.API_INVALID_FILE_TYPE, filename=filename, extension=file_ext
            )
            raise ValueError(codes.MSG_API_INVALID_FILE_TYPE)

    def validate_size(self, content: bytes, filename: str) -> None:
        """
        Validate file size is within limits.

        Args:
            content: File content bytes
            filename: Name of file

        Raises:
            ValueError: If file too large
        """
        file_size_mb = len(content) / BYTES_PER_MB

        if file_size_mb > self.config.storage.max_file_size_mb:
            logger.warning(
                codes.API_FILE_TOO_LARGE,
                filename=filename,
                size_mb=file_size_mb,
                max_mb=self.config.storage.max_file_size_mb,
            )
            raise ValueError(codes.MSG_API_FILE_TOO_LARGE)
