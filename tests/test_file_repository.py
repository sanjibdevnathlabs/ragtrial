"""
Tests for app/modules/file/repository.py - FileRepository data access.

Tests repository operations with proper database mocking.
"""

from unittest.mock import Mock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.modules.file.entity import File
from app.modules.file.repository import FileRepository
from database.exceptions import DatabaseQueryError


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
        mock_query_chain.scalar.return_value = 0
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
def mock_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def repository():
    """Create FileRepository instance."""
    return FileRepository()


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


class TestFileRepositoryBasicQueries:
    """Test basic query methods."""

    def test_find_by_filename(self, repository, mock_session, sample_file):
        """Test finding file by filename."""
        with patch.object(repository, "find_by_field", return_value=sample_file):
            result = repository.find_by_filename(mock_session, "test.pdf")

            assert result == sample_file
            repository.find_by_field.assert_called_once_with(
                mock_session, "filename", "test.pdf", False
            )

    def test_find_by_filename_with_deleted(self, repository, mock_session):
        """Test finding file by filename including deleted."""
        with patch.object(repository, "find_by_field", return_value=None):
            result = repository.find_by_filename(
                mock_session, "test.pdf", include_deleted=True
            )

            assert result is None
            repository.find_by_field.assert_called_once_with(
                mock_session, "filename", "test.pdf", True
            )

    def test_find_by_checksum(self, repository, mock_session, sample_file):
        """Test finding file by checksum."""
        with patch.object(repository, "find_by_field", return_value=sample_file):
            result = repository.find_by_checksum(mock_session, "abc123")

            assert result == sample_file
            repository.find_by_field.assert_called_once_with(
                mock_session, "checksum", "abc123", False
            )

    def test_find_by_checksum_not_found(self, repository, mock_session):
        """Test finding file by checksum when not found."""
        with patch.object(repository, "find_by_field", return_value=None):
            result = repository.find_by_checksum(mock_session, "xyz789")

            assert result is None


class TestFileRepositoryIndexingQueries:
    """Test indexing-related queries."""

    def test_find_unindexed_files_no_limit(self, repository, mock_session, sample_file):
        """Test finding unindexed files without limit."""
        with patch.object(repository, "find_by_fields", return_value=[sample_file]):
            result = repository.find_unindexed_files(mock_session)

            assert len(result) == 1
            assert result[0] == sample_file
            repository.find_by_fields.assert_called_once_with(
                mock_session, filters={"indexed": False}, include_deleted=False
            )

    def test_find_unindexed_files_with_limit(self, repository, mock_session, sample_file):
        """Test finding unindexed files with limit."""
        with patch.object(
            repository, "find_by_fields", return_value=[sample_file, sample_file]
        ):
            result = repository.find_unindexed_files(mock_session, limit=1)

            assert len(result) == 1
            repository.find_by_fields.assert_called_once()

    def test_find_indexed_files_no_limit(self, repository, mock_session, sample_file):
        """Test finding indexed files without limit."""
        sample_file.indexed = True
        with patch.object(repository, "find_by_fields", return_value=[sample_file]):
            result = repository.find_indexed_files(mock_session)

            assert len(result) == 1
            assert result[0].indexed is True

    def test_find_indexed_files_with_limit(self, repository, mock_session, sample_file):
        """Test finding indexed files with limit."""
        sample_file.indexed = True
        with patch.object(
            repository, "find_by_fields", return_value=[sample_file, sample_file]
        ):
            result = repository.find_indexed_files(mock_session, limit=1)

            assert len(result) == 1


class TestFileRepositoryMarkAsIndexed:
    """Test mark_as_indexed operation."""

    def test_mark_as_indexed_success(self, repository, mock_session, sample_file):
        """Test successfully marking file as indexed."""
        with patch.object(
            repository, "find_by_id", return_value=sample_file
        ), patch.object(repository, "update", return_value=sample_file):
            result = repository.mark_as_indexed(mock_session, "file-123")

            assert result is True
            repository.find_by_id.assert_called_once_with(mock_session, "file-123")
            repository.update.assert_called_once()

    def test_mark_as_indexed_not_found(self, repository, mock_session):
        """Test marking non-existent file as indexed."""
        with patch.object(repository, "find_by_id", return_value=None), patch(
            "app.modules.file.repository.logger"
        ), patch("app.modules.file.repository.codes") as mock_codes:
            mock_codes.DB_ENTITY_NOT_FOUND = "DB_ENTITY_NOT_FOUND"
            result = repository.mark_as_indexed(mock_session, "nonexistent")

            assert result is False
            repository.find_by_id.assert_called_once()

    def test_mark_as_indexed_error(self, repository, mock_session, sample_file):
        """Test mark_as_indexed with database error."""
        with patch.object(
            repository, "find_by_id", return_value=sample_file
        ), patch.object(
            repository, "update", side_effect=SQLAlchemyError("Database error")
        ):
            with pytest.raises(DatabaseQueryError) as exc_info:
                repository.mark_as_indexed(mock_session, "file-123")

            assert "Database error" in str(exc_info.value.original_error)


class TestFileRepositoryTotalSize:
    """Test get_total_size operation."""

    def test_get_total_size_with_files(self, repository, mock_session):
        """Test getting total size when files exist."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 10240
        mock_session.query.return_value = mock_query

        result = repository.get_total_size(mock_session)

        assert result == 10240

    def test_get_total_size_empty(self, repository, mock_session):
        """Test getting total size when no files exist."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        mock_session.query.return_value = mock_query

        result = repository.get_total_size(mock_session)

        assert result == 0

    def test_get_total_size_include_deleted(self, repository, mock_session):
        """Test getting total size including deleted files."""
        mock_query = MagicMock()
        mock_query.scalar.return_value = 20480
        mock_session.query.return_value = mock_query

        result = repository.get_total_size(mock_session, include_deleted=True)

        assert result == 20480
        # Verify filter was NOT called when include_deleted=True
        mock_query.filter.assert_not_called()

    def test_get_total_size_error(self, repository, mock_session):
        """Test get_total_size with database error."""
        mock_session.query.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(DatabaseQueryError) as exc_info:
            repository.get_total_size(mock_session)

        assert "Database error" in str(exc_info.value.original_error)


class TestFileRepositoryFilterQueries:
    """Test filtering queries."""

    def test_find_by_storage_backend(self, repository, mock_session, sample_file):
        """Test finding files by storage backend."""
        with patch.object(repository, "find_by_fields", return_value=[sample_file]):
            result = repository.find_by_storage_backend(mock_session, "local")

            assert len(result) == 1
            assert result[0].storage_backend == "local"
            repository.find_by_fields.assert_called_once_with(
                mock_session,
                filters={"storage_backend": "local"},
                include_deleted=False,
            )

    def test_find_by_storage_backend_include_deleted(
        self, repository, mock_session, sample_file
    ):
        """Test finding files by storage backend including deleted."""
        with patch.object(repository, "find_by_fields", return_value=[sample_file]):
            result = repository.find_by_storage_backend(
                mock_session, "s3", include_deleted=True
            )

            repository.find_by_fields.assert_called_once_with(
                mock_session, filters={"storage_backend": "s3"}, include_deleted=True
            )

    def test_find_by_file_type(self, repository, mock_session, sample_file):
        """Test finding files by file type."""
        with patch.object(repository, "find_by_fields", return_value=[sample_file]):
            result = repository.find_by_file_type(mock_session, "pdf")

            assert len(result) == 1
            assert result[0].file_type == "pdf"
            repository.find_by_fields.assert_called_once_with(
                mock_session, filters={"file_type": "pdf"}, include_deleted=False
            )

    def test_find_by_file_type_include_deleted(
        self, repository, mock_session, sample_file
    ):
        """Test finding files by file type including deleted."""
        with patch.object(repository, "find_by_fields", return_value=[sample_file]):
            result = repository.find_by_file_type(
                mock_session, "txt", include_deleted=True
            )

            repository.find_by_fields.assert_called_once_with(
                mock_session, filters={"file_type": "txt"}, include_deleted=True
            )

