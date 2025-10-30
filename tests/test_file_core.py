"""
Tests for app/modules/file/core.py - FileService business logic.

Tests file service operations with proper database mocking.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.file.core import FileService
from app.modules.file.entity import File


@pytest.fixture(scope="module", autouse=True)
def mock_health_dependencies():
    """Mock health check dependencies to prevent real API calls."""
    from app.modules.health.service import HealthService
    from database.session import SessionFactory

    if hasattr(HealthService, "_instances"):
        HealthService._instances.clear()
    if hasattr(SessionFactory, "_instances"):
        SessionFactory._instances.clear()

    with patch.object(HealthService, "_test_llm_api", return_value=True), patch.object(
        HealthService, "_test_embeddings_api", return_value=True
    ), patch("app.modules.health.service.create_embeddings") as mock_embeddings, patch(
        "app.modules.health.service.create_vectorstore"
    ) as mock_vectorstore, patch(
        "database.session.SessionFactory.check_health", return_value=True
    ), patch(
        "database.session.SessionFactory.get_read_session"
    ) as mock_read_session_global, patch(
        "database.session.SessionFactory.get_write_session"
    ) as mock_write_session_global:

        mock_embeddings_instance = Mock()
        mock_embeddings_instance.embed_query.return_value = [0.1] * 768
        mock_embeddings.return_value = mock_embeddings_instance

        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vectorstore.return_value = mock_vs_instance

        # Mock database sessions
        mock_session = MagicMock()
        mock_query_chain = MagicMock()
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.order_by.return_value = mock_query_chain
        mock_query_chain.limit.return_value = mock_query_chain
        mock_query_chain.offset.return_value = mock_query_chain
        mock_query_chain.all.return_value = []
        mock_query_chain.first.return_value = None
        mock_session.query.return_value = mock_query_chain

        read_context = MagicMock()
        read_context.__enter__.return_value = mock_session
        read_context.__exit__.return_value = None
        mock_read_session_global.return_value = read_context

        write_context = MagicMock()
        write_context.__enter__.return_value = mock_session
        write_context.__exit__.return_value = None
        mock_write_session_global.return_value = write_context

        yield

        if hasattr(HealthService, "_instances"):
            HealthService._instances.clear()
        if hasattr(SessionFactory, "_instances"):
            SessionFactory._instances.clear()


@pytest.fixture
def mock_session_factory():
    """Mock SessionFactory."""
    from unittest.mock import MagicMock

    factory = Mock()
    mock_read_session = MagicMock()
    mock_write_session = MagicMock()

    # Create context managers
    read_context = MagicMock()
    read_context.__enter__.return_value = mock_read_session
    read_context.__exit__.return_value = None

    write_context = MagicMock()
    write_context.__enter__.return_value = mock_write_session
    write_context.__exit__.return_value = None

    factory.get_read_session.return_value = read_context
    factory.get_write_session.return_value = write_context

    return factory, mock_read_session, mock_write_session


@pytest.fixture
def mock_repository():
    """Mock FileRepository."""
    return Mock()


@pytest.fixture
def file_service(mock_session_factory, mock_repository):
    """Create FileService with mocked dependencies."""
    factory, _, _ = mock_session_factory
    service = FileService()
    service.session_factory = factory
    service.repository = mock_repository
    return service


@pytest.fixture
def sample_file():
    """Create a sample File entity."""
    return File(
        id="file-123",
        filename="test.pdf",
        file_path="storage/test.pdf",
        file_type="pdf",
        file_size=1024,
        checksum="abc123",
        storage_backend="local",
        indexed=False,
    )


class TestFileServiceChecksum:
    """Test checksum calculation."""

    def test_calculate_checksum_success(self):
        """Test successful checksum calculation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            checksum = FileService.calculate_checksum(temp_path)
            assert isinstance(checksum, str)
            assert len(checksum) == 64  # SHA-256 hex digest length
            # Verify it's consistent
            checksum2 = FileService.calculate_checksum(temp_path)
            assert checksum == checksum2
        finally:
            Path(temp_path).unlink()

    def test_calculate_checksum_large_file(self):
        """Test checksum calculation for large file (tests chunking)."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # Write 10KB of data (more than 8192 chunk size)
            f.write(b"x" * 10240)
            temp_path = f.name

        try:
            checksum = FileService.calculate_checksum(temp_path)
            assert isinstance(checksum, str)
            assert len(checksum) == 64
        finally:
            Path(temp_path).unlink()


class TestFileServiceDuplicateCheck:
    """Test duplicate detection."""

    def test_check_duplicate_exists(
        self, file_service, mock_session_factory, mock_repository, sample_file
    ):
        """Test duplicate check when file exists."""
        _, mock_read_session, _ = mock_session_factory
        mock_repository.find_by_checksum.return_value = sample_file

        result = file_service.check_duplicate("abc123")

        assert result is not None
        assert result["filename"] == "test.pdf"
        mock_repository.find_by_checksum.assert_called_once_with(
            mock_read_session, "abc123"
        )

    def test_check_duplicate_not_exists(self, file_service, mock_repository):
        """Test duplicate check when file doesn't exist."""
        mock_repository.find_by_checksum.return_value = None

        result = file_service.check_duplicate("xyz789")

        assert result is None
        mock_repository.find_by_checksum.assert_called_once()


class TestFileServiceCreateRecord:
    """Test file record creation."""

    def test_create_file_record_success(self, file_service, mock_repository, sample_file):
        """Test successful file record creation."""
        mock_repository.create.return_value = sample_file

        result = file_service.create_file_record(
            filename="test.pdf",
            file_path="storage/test.pdf",
            file_size=1024,
            checksum="abc123",
            storage_backend="local",
        )

        assert result["filename"] == "test.pdf"
        assert result["file_size"] == 1024
        mock_repository.create.assert_called_once()

    def test_create_file_record_duplicate_checksum(
        self, file_service, mock_repository, sample_file
    ):
        """Test file record creation with duplicate checksum."""
        # First call (create) raises IntegrityError
        mock_repository.create.side_effect = IntegrityError(
            "statement", "params", "orig"
        )
        # Second call (find_by_checksum) returns existing file
        mock_repository.find_by_checksum.return_value = sample_file

        with pytest.raises(ValueError) as exc_info:
            file_service.create_file_record(
                filename="duplicate.pdf",
                file_path="storage/duplicate.pdf",
                file_size=2048,
                checksum="abc123",
                storage_backend="local",
            )

        assert "test.pdf" in str(exc_info.value)
        mock_repository.create.assert_called_once()
        mock_repository.find_by_checksum.assert_called_once()

    def test_create_file_record_generic_error(self, file_service, mock_repository):
        """Test file record creation with generic error."""
        mock_repository.create.side_effect = Exception("Database error")

        with pytest.raises(Exception) as exc_info:
            file_service.create_file_record(
                filename="test.pdf",
                file_path="storage/test.pdf",
                file_size=1024,
                checksum="abc123",
            )

        assert "Database error" in str(exc_info.value)


class TestFileServiceRetrieval:
    """Test file retrieval operations."""

    def test_get_file_by_id_found(self, file_service, mock_repository, sample_file):
        """Test getting file by ID when found."""
        mock_repository.find_by_id.return_value = sample_file

        result = file_service.get_file_by_id("file-123")

        assert result is not None
        assert result["id"] == "file-123"
        mock_repository.find_by_id.assert_called_once()

    def test_get_file_by_id_not_found(self, file_service, mock_repository):
        """Test getting file by ID when not found."""
        mock_repository.find_by_id.return_value = None

        result = file_service.get_file_by_id("nonexistent")

        assert result is None

    def test_get_file_by_filename_found(
        self, file_service, mock_repository, sample_file
    ):
        """Test getting file by filename when found."""
        mock_repository.find_by_filename.return_value = sample_file

        result = file_service.get_file_by_filename("test.pdf")

        assert result is not None
        assert result["filename"] == "test.pdf"

    def test_get_file_by_filename_not_found(self, file_service, mock_repository):
        """Test getting file by filename when not found."""
        mock_repository.find_by_filename.return_value = None

        result = file_service.get_file_by_filename("nonexistent.pdf")

        assert result is None


class TestFileServiceListing:
    """Test file listing operations."""

    def test_list_all_files(self, file_service, mock_repository, sample_file):
        """Test listing all files."""
        mock_repository.find_all.return_value = [sample_file]

        result = file_service.list_all_files()

        assert len(result) == 1
        assert result[0]["filename"] == "test.pdf"
        mock_repository.find_all.assert_called_once()

    def test_list_all_files_with_pagination(
        self, file_service, mock_repository, sample_file
    ):
        """Test listing files with pagination."""
        mock_repository.find_all.return_value = [sample_file]

        result = file_service.list_all_files(limit=10, offset=0)

        assert len(result) == 1
        call_args = mock_repository.find_all.call_args
        assert call_args.kwargs["limit"] == 10
        assert call_args.kwargs["offset"] == 0

    def test_list_all_files_empty(self, file_service, mock_repository):
        """Test listing files when none exist."""
        mock_repository.find_all.return_value = []

        result = file_service.list_all_files()

        assert len(result) == 0


class TestFileServiceDeletion:
    """Test file deletion operations."""

    def test_delete_file_success(
        self, file_service, mock_session_factory, mock_repository
    ):
        """Test successful file deletion."""
        _, _, mock_write_session = mock_session_factory
        mock_repository.delete.return_value = True

        result = file_service.delete_file("file-123")

        assert result is True
        mock_repository.delete.assert_called_once_with(mock_write_session, "file-123")

    def test_delete_file_not_found(self, file_service, mock_repository):
        """Test deleting non-existent file."""
        mock_repository.delete.return_value = False

        result = file_service.delete_file("nonexistent")

        assert result is False


class TestFileServiceIndexing:
    """Test indexing-related operations."""

    def test_mark_as_indexed_success(self, file_service, mock_repository):
        """Test marking file as indexed."""
        mock_repository.mark_as_indexed.return_value = True

        result = file_service.mark_as_indexed("file-123")

        assert result is True
        mock_repository.mark_as_indexed.assert_called_once()

    def test_mark_as_indexed_not_found(self, file_service, mock_repository):
        """Test marking non-existent file as indexed."""
        mock_repository.mark_as_indexed.return_value = False

        result = file_service.mark_as_indexed("nonexistent")

        assert result is False

    def test_get_unindexed_files(self, file_service, mock_repository, sample_file):
        """Test getting unindexed files."""
        sample_file.indexed = False
        mock_repository.find_unindexed_files.return_value = [sample_file]

        result = file_service.get_unindexed_files()

        assert len(result) == 1
        assert result[0]["indexed"] is False

    def test_get_unindexed_files_with_limit(
        self, file_service, mock_session_factory, mock_repository, sample_file
    ):
        """Test getting unindexed files with limit."""
        _, mock_read_session, _ = mock_session_factory
        mock_repository.find_unindexed_files.return_value = [sample_file]

        result = file_service.get_unindexed_files(limit=5)

        assert len(result) == 1
        mock_repository.find_unindexed_files.assert_called_once_with(
            mock_read_session, limit=5
        )

    def test_get_indexed_files(self, file_service, mock_repository, sample_file):
        """Test getting indexed files."""
        sample_file.indexed = True
        mock_repository.find_indexed_files.return_value = [sample_file]

        result = file_service.get_indexed_files()

        assert len(result) == 1
        assert result[0]["indexed"] is True

    def test_get_indexed_files_with_limit(
        self, file_service, mock_session_factory, mock_repository, sample_file
    ):
        """Test getting indexed files with limit."""
        _, mock_read_session, _ = mock_session_factory
        mock_repository.find_indexed_files.return_value = [sample_file]

        result = file_service.get_indexed_files(limit=10)

        assert len(result) == 1
        mock_repository.find_indexed_files.assert_called_once_with(
            mock_read_session, limit=10
        )


class TestFileServiceStatistics:
    """Test statistics operations."""

    def test_get_total_size(self, file_service, mock_repository):
        """Test getting total file size."""
        mock_repository.get_total_size.return_value = 10240

        result = file_service.get_total_size()

        assert result == 10240
        mock_repository.get_total_size.assert_called_once()

    def test_get_statistics(self, file_service, mock_repository, sample_file):
        """Test getting file statistics."""
        mock_repository.count.return_value = 10
        mock_repository.find_indexed_files.return_value = [sample_file] * 7
        mock_repository.get_total_size.return_value = 10485760  # 10 MB

        result = file_service.get_statistics()

        assert result["total_files"] == 10
        assert result["indexed_files"] == 7
        assert result["unindexed_files"] == 3
        assert result["total_size_bytes"] == 10485760
        assert result["total_size_mb"] == 10.0

    def test_get_statistics_empty(self, file_service, mock_repository):
        """Test getting statistics when no files exist."""
        mock_repository.count.return_value = 0
        mock_repository.find_indexed_files.return_value = []
        mock_repository.get_total_size.return_value = 0

        result = file_service.get_statistics()

        assert result["total_files"] == 0
        assert result["indexed_files"] == 0
        assert result["unindexed_files"] == 0
        assert result["total_size_bytes"] == 0
        assert result["total_size_mb"] == 0.0

