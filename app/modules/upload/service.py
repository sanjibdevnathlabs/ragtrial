"""
Upload service.

Handles file upload operations with database integration.
"""

import hashlib
import trace.codes as codes

import constants
from app.modules.file.core import FileService as DBFileService
from app.modules.file.entity import File
from app.modules.upload.response import UploadResponse
from app.modules.upload.validators import UploadValidator
from config import Config
from logger import get_logger
from storage_backend.base import StorageProtocol
from utils.singleton import SingletonMeta

logger = get_logger(__name__)


class UploadService(metaclass=SingletonMeta):
    """
    Singleton service for file upload operations.

    Uses database for metadata storage and duplicate detection.
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
        if not hasattr(self, "_initialized"):
            self.config = config
            self.storage = storage
            self.validator = UploadValidator(config)
            self.db_file_service = DBFileService()
            self._initialized = True

    def upload_file(self, filename: str, content: bytes) -> UploadResponse:
        """
        Upload file to storage with database metadata.

        Process:
        1. Validate file
        2. Calculate checksum
        3. Generate UUID for storage
        4. Store with UUID-based name
        5. Create database record (with atomic duplicate check)

        Note: Duplicate checking is now done atomically inside create_file_record
        using SELECT ... FOR UPDATE to prevent deadlocks during parallel uploads.

        Args:
            filename: Original filename
            content: File content bytes

        Returns:
            UploadResponse: Upload result with full metadata

        Raises:
            ValueError: If validation fails or duplicate exists
            Exception: If upload fails
        """
        logger.info(codes.API_UPLOAD_STARTED, filename=filename)

        self._validate_file(filename, content)
        checksum = self._calculate_checksum(content)

        file_id = File.generate_id()
        file_type = File.get_file_type_from_filename(filename)
        storage_filename = f"{file_id}.{file_type}"
        file_path = self._store_file(storage_filename, content)

        try:
            file_record = self.db_file_service.create_file_record(
                filename=filename,
                file_path=file_path,
                file_size=len(content),
                checksum=checksum,
                storage_backend=self.config.storage.backend,
            )
        except ValueError as e:
            logger.warning(
                codes.API_UPLOAD_FAILED,
                filename=filename,
                reason=constants.ERROR_FILE_DUPLICATE,
                error=str(e),
            )
            try:
                self.storage.delete_file(file_path)
            except Exception as cleanup_error:
                logger.error(
                    codes.API_UPLOAD_FAILED,
                    error=f"Failed to cleanup file after duplicate: {cleanup_error}",
                )
            raise

        logger.info(
            codes.API_UPLOAD_COMPLETED,
            file_id=file_record["id"],
            filename=filename,
            path=file_path,
            size_bytes=len(content),
            checksum=checksum[:16],
            backend=self.config.storage.backend,
        )

        return UploadResponse(
            success=True,
            file_id=file_record["id"],
            filename=file_record["filename"],
            path=file_record["file_path"],
            size=file_record["file_size"],
            file_type=file_record["file_type"],
            checksum=file_record["checksum"],
            backend=file_record["storage_backend"],
            indexed=file_record["indexed"],
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

    def _calculate_checksum(self, content: bytes) -> str:
        """
        Calculate SHA-256 checksum of content.

        Args:
            content: File content bytes

        Returns:
            Hex digest checksum
        """
        return hashlib.sha256(content).hexdigest()

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
            return self.storage.upload_file(content, filename)
        except Exception as e:
            logger.error(
                codes.API_UPLOAD_FAILED, filename=filename, error=str(e), exc_info=True
            )
            raise
