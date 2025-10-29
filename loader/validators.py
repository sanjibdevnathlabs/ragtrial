"""
Document Loader Validators.

Handles all validation logic for document loading.
Follows Single Responsibility Principle - validation only.
"""

import trace.codes as codes
from pathlib import Path

import constants
from logger.setup import get_logger

logger = get_logger(__name__)


class LoaderValidator:
    """Validator for document loader operations.

    Centralizes all validation logic with clear, testable methods.
    Each method validates one specific condition.
    """

    @staticmethod
    def validate_file_exists(file_path: Path) -> None:
        """Validate that file exists.

        Args:
            file_path: Path to file

        Raises:
            FileNotFoundError: If file does not exist
        """
        if not file_path.exists():
            logger.error(codes.LOADER_FILE_NOT_FOUND, file_path=str(file_path))
            raise FileNotFoundError(f"{constants.ERROR_FILE_NOT_FOUND}: {file_path}")

    @staticmethod
    def validate_file_supported(file_path: Path, is_supported_fn) -> None:
        """Validate that file type is supported.

        Args:
            file_path: Path to file
            is_supported_fn: Function to check if extension is supported

        Raises:
            ValueError: If file type is not supported
        """
        if not is_supported_fn(file_path):
            logger.error(codes.LOADER_UNSUPPORTED_FORMAT, extension=file_path.suffix)
            raise ValueError(
                f"{constants.ERROR_UNSUPPORTED_FORMAT}: {file_path.suffix}"
            )

    @staticmethod
    def validate_documents_loaded(documents, file_path: Path) -> None:
        """Validate that documents were loaded.

        Args:
            documents: List of loaded documents
            file_path: Path to file

        Raises:
            ValueError: If no documents were loaded
        """
        if not documents:
            logger.warning(codes.LOADER_EMPTY_DOCUMENT, file_path=str(file_path))
            raise ValueError(f"{constants.ERROR_EMPTY_DOCUMENT}: {file_path}")
