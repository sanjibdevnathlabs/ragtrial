"""
Router tests for files endpoint.

Tests the FastAPI router layer with proper request/response handling.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.modules.files.response import FileListResponse, FileMetadataResponse


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
    ) as mock_read_session:

        mock_embeddings_instance = Mock()
        mock_embeddings_instance.embed_query.return_value = [0.1] * 768
        mock_embeddings.return_value = mock_embeddings_instance

        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vectorstore.return_value = mock_vs_instance

        mock_session = Mock()
        mock_query_chain = Mock()
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.order_by.return_value = mock_query_chain
        mock_query_chain.limit.return_value = mock_query_chain
        mock_query_chain.offset.return_value = mock_query_chain
        mock_query_chain.all.return_value = []
        mock_query_chain.first.return_value = None
        mock_session.query.return_value = mock_query_chain
        mock_read_session.return_value.__enter__.return_value = mock_session
        mock_read_session.return_value.__exit__.return_value = None

        yield

        if hasattr(HealthService, "_instances"):
            HealthService._instances.clear()
        if hasattr(SessionFactory, "_instances"):
            SessionFactory._instances.clear()


@pytest.fixture
def mock_file_service():
    """Mock file service."""
    service = Mock()
    service.list_files.return_value = FileListResponse(
        files=[
            {
                "file_id": "file-id-1",
                "filename": "test1.pdf",
                "file_size": 1024,
                "indexed": False,
            },
            {
                "file_id": "file-id-2",
                "filename": "test2.pdf",
                "file_size": 2048,
                "indexed": False,
            },
        ],
        count=2,
        backend="local",
    )
    service.get_file_metadata.return_value = FileMetadataResponse(
        file_id="file-id-1",
        filename="test.pdf",
        file_path="source_docs/test.pdf",
        file_type="pdf",
        file_size=1024,
        checksum="abc123",
        storage_backend="local",
        indexed=False,
        created_at=1700000000000,
        updated_at=1700000000000,
    )
    service.delete_file.return_value = {
        "success": True,
        "message": "File deleted successfully",
        "filename": "test.pdf",
    }
    return service


@pytest.fixture
def client(mock_file_service):
    """Create test client with mocked dependencies."""
    from app.api.dependencies import get_file_service
    from app.api.main import app

    # Override the dependency
    app.dependency_overrides[get_file_service] = lambda: mock_file_service

    yield TestClient(app)

    # Clean up
    app.dependency_overrides.clear()


class TestFilesRouterList:
    """Test file listing via router."""

    def test_list_files_success(self, client, mock_file_service):
        """Test successful file listing."""
        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["files"]) == 2
        assert data["files"][0]["filename"] == "test1.pdf"
        mock_file_service.list_files.assert_called_once()

    def test_list_files_empty(self, client, mock_file_service):
        """Test listing files when none exist."""
        mock_file_service.list_files.return_value = FileListResponse(
            files=[], count=0, backend="local"
        )

        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert len(data["files"]) == 0

    def test_list_files_server_error(self, client, mock_file_service):
        """Test listing files with server error."""
        mock_file_service.list_files.side_effect = Exception("Database error")

        response = client.get("/api/v1/files")

        assert response.status_code == 500
        data = response.json()
        assert "error_code" in data["detail"]
        assert data["detail"]["error_code"] == "LIST_ERROR"


class TestFilesRouterMetadata:
    """Test file metadata retrieval via router."""

    def test_get_file_metadata_success(self, client, mock_file_service):
        """Test successful metadata retrieval."""
        response = client.get("/api/v1/files/test.pdf")

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert data["file_size"] == 1024
        assert data["file_type"] == "pdf"
        assert data["checksum"] == "abc123"
        assert data["storage_backend"] == "local"
        mock_file_service.get_file_metadata.assert_called_once_with("test.pdf")

    def test_get_file_metadata_not_found(self, client, mock_file_service):
        """Test metadata retrieval for non-existent file."""
        mock_file_service.get_file_metadata.side_effect = FileNotFoundError(
            "File not found"
        )

        response = client.get("/api/v1/files/nonexistent.pdf")

        assert response.status_code == 404
        data = response.json()
        assert "error_code" in data["detail"]
        assert data["detail"]["error_code"] == "FILE_NOT_FOUND"

    def test_get_file_metadata_server_error(self, client, mock_file_service):
        """Test metadata retrieval with server error."""
        mock_file_service.get_file_metadata.side_effect = Exception("Database error")

        response = client.get("/api/v1/files/test.pdf")

        assert response.status_code == 500
        data = response.json()
        assert "error_code" in data["detail"]
        assert data["detail"]["error_code"] == "METADATA_ERROR"


class TestFilesRouterDelete:
    """Test file deletion via router."""

    def test_delete_file_success(self, client, mock_file_service):
        """Test successful file deletion."""
        response = client.delete("/api/v1/files/test.pdf")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["filename"] == "test.pdf"
        mock_file_service.delete_file.assert_called_once_with("test.pdf")

    def test_delete_file_not_found(self, client, mock_file_service):
        """Test deletion of non-existent file."""
        mock_file_service.delete_file.side_effect = FileNotFoundError("File not found")

        response = client.delete("/api/v1/files/nonexistent.pdf")

        assert response.status_code == 404
        data = response.json()
        assert "error_code" in data["detail"]
        assert data["detail"]["error_code"] == "FILE_NOT_FOUND"

    def test_delete_file_server_error(self, client, mock_file_service):
        """Test file deletion with server error."""
        mock_file_service.delete_file.side_effect = Exception("Storage error")

        response = client.delete("/api/v1/files/test.pdf")

        assert response.status_code == 500
        data = response.json()
        assert "error_code" in data["detail"]
        assert data["detail"]["error_code"] == "DELETE_ERROR"

