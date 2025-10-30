"""
Integration tests for API endpoints.

INTEGRATION TESTS - These tests require real database and external services.
They test the full request/response flow with actual database backend.

These tests are marked with @pytest.mark.integration and are skipped
during unit test runs. Run with: make test-integration

Test Coverage:
- Health endpoint with database
- Upload endpoint with storage
- List files endpoint with database
- File metadata endpoint with database
"""

import uuid

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.api.main import app
from app.modules.file.core import FileService as DBFileService
from database.session import SessionFactory


@pytest.fixture(scope="function")
def db_session():
    """
    Provide transactional database session for each test.

    Strategy:
    - Create connection and start nested transaction (savepoint)
    - Bind session to this transactional connection
    - Mock commit() to do nothing (just flush)
    - Yield session for test to use
    - Rollback transaction (NEVER commit)
    - Close session and connection

    Benefits:
    - Perfect isolation between parallel tests
    - No data persists in database
    - Fast (rollback is instant)
    - No cleanup needed
    """

    from sqlalchemy.orm import Session

    session_factory = SessionFactory()
    engine = session_factory.get_write_engine()

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    original_commit = session.commit

    def mock_commit():
        session.flush()  # Write to transaction but don't commit

    session.commit = mock_commit

    yield session

    session.commit = original_commit
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def override_db_dependency(db_session):
    """
    Override SessionFactory to use our transactional session.

    This ensures ALL database operations in the app use our
    test transaction, which gets rolled back after the test.

    Benefits:
    - Perfect isolation for parallel tests
    - No data persists in database
    - No manual cleanup needed
    """
    from contextlib import contextmanager
    from unittest.mock import MagicMock, patch

    @contextmanager
    def mock_write_session():
        yield db_session

    @contextmanager
    def mock_read_session():
        yield db_session

    mock_factory = MagicMock()
    mock_factory.get_write_session = mock_write_session
    mock_factory.get_read_session = mock_read_session
    mock_factory.get_write_engine = lambda: db_session.get_bind()
    mock_factory.get_read_engine = lambda: db_session.get_bind()

    with patch("database.session.SessionFactory", return_value=mock_factory):
        with patch("app.modules.file.core.SessionFactory", return_value=mock_factory):
            yield

    # No cleanup needed - handled by db_session fixture


@pytest.fixture
def db_file_service():
    """Get database file service."""
    return DBFileService()


@pytest.fixture
def sample_integration_files(db_file_service):
    """
    Create sample files in database for integration tests.

    Uses uuid4() for checksums to ensure uniqueness in parallel test execution.
    This prevents deadlocks when multiple test workers try to insert files
    with the same checksum simultaneously.
    """
    unique_id = str(uuid.uuid4())

    files_data = [
        {
            "filename": "file1.pdf",
            "file_path": "source_docs/integration-uuid1.pdf",
            "file_size": 1024,
            "checksum": f"integration_checksum1_{unique_id}",
            "storage_backend": "local",
        },
        {
            "filename": "file2.txt",
            "file_path": "source_docs/integration-uuid2.txt",
            "file_size": 2048,
            "checksum": f"integration_checksum2_{unique_id}",
            "storage_backend": "local",
        },
    ]

    created_files = []
    for file_data in files_data:
        file_record = db_file_service.create_file_record(**file_data)
        created_files.append(file_record)

    return created_files


@pytest.fixture
def mock_storage():
    """Mock storage backend for integration tests."""
    storage = Mock()
    storage.upload_file.return_value = "source_docs/test.pdf"
    storage.delete_file.return_value = None
    return storage


@pytest.fixture(scope="module", autouse=True)
def mock_health_dependencies():
    """
    Mock ALL health check dependencies at module level to prevent real API calls.
    
    This fixture uses autouse=True to ensure it's ALWAYS applied for integration tests.
    
    CRITICAL: Integration tests should NEVER connect to:
    - Real ChromaDB (vectorstore) - disk I/O issues
    - Real LLM APIs (Google Gemini) - costs money + quota limits
    - Real Embeddings APIs (Google) - costs money + quota limits
    """
    # Reset HealthService singleton to ensure clean state
    from app.modules.health.service import HealthService
    if hasattr(HealthService, '_instances'):
        HealthService._instances.clear()
    
    # Patch internal health check methods directly
    with patch.object(HealthService, '_test_llm_api', return_value=True), \
         patch.object(HealthService, '_test_embeddings_api', return_value=True), \
         patch("app.modules.health.service.create_embeddings") as mock_embeddings, \
         patch("app.modules.health.service.create_vectorstore") as mock_vectorstore:
        
        # Mock Embeddings to return success
        mock_embeddings_instance = Mock()
        mock_embeddings_instance.embed_query.return_value = [0.1] * 768
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock Vectorstore to return success
        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vectorstore.return_value = mock_vs_instance
        
        yield
        
        # Clean up singleton after module
        if hasattr(HealthService, '_instances'):
            HealthService._instances.clear()


@pytest.fixture
def client(mock_storage, override_db_dependency):
    """
    Create test client with mocked storage and transactional database.

    The override_db_dependency fixture ensures all database operations
    happen within a transaction that gets rolled back after the test.
    This provides perfect isolation for parallel test execution.
    
    The mock_health_dependencies fixture (autouse=True) ensures we don't
    connect to real external services (ChromaDB, LLM APIs, Embeddings APIs).
    """
    with patch("app.api.dependencies.create_storage", return_value=mock_storage):
        yield TestClient(app)


class TestHealthEndpoint:
    """Test suite for health endpoint."""

    def test_health_returns_200(self, client):
        """Test health endpoint returns 200 OK."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Test health endpoint returns JSON."""
        response = client.get("/api/v1/health")

        assert response.headers["content-type"] == "application/json"

    def test_health_includes_status(self, client):
        """Test health response includes status."""
        response = client.get("/api/v1/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_includes_components(self, client):
        """Test health response includes components array."""
        response = client.get("/api/v1/health")
        data = response.json()

        assert "components" in data
        assert isinstance(data["components"], list)
        assert len(data["components"]) == 4  # database, vectorstore, llm, embeddings

    def test_health_includes_version(self, client):
        """Test health response includes version."""
        response = client.get("/api/v1/health")
        data = response.json()

        assert "version" in data


class TestUploadEndpoint:
    """Test suite for upload endpoint."""

    def test_upload_returns_200(self, client, mock_storage):
        """Test upload endpoint returns 200 OK."""
        content = f"test content {uuid.uuid4()}".encode()
        files = {"file": ("test.pdf", content, "application/pdf")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 200

    def test_upload_returns_success_response(self, client, mock_storage):
        """Test upload returns success response."""
        content = f"test content {uuid.uuid4()}".encode()
        files = {"file": ("test.pdf", content, "application/pdf")}

        response = client.post("/api/v1/upload", files=files)
        data = response.json()

        assert data["success"] is True

    def test_upload_includes_filename(self, client, mock_storage):
        """Test upload response includes filename."""
        content = f"test content {uuid.uuid4()}".encode()
        files = {"file": ("test.pdf", content, "application/pdf")}

        response = client.post("/api/v1/upload", files=files)
        data = response.json()

        assert data["filename"] == "test.pdf"

    def test_upload_rejects_invalid_extension(self, client, mock_storage):
        """Test upload rejects invalid file extension."""
        files = {"file": ("virus.exe", b"bad content", "application/octet-stream")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400


class TestListFilesEndpoint:
    """Test suite for list files endpoint."""

    def test_list_files_returns_200(self, client, sample_integration_files):
        """Test list files endpoint returns 200 OK."""
        response = client.get("/api/v1/files")

        assert response.status_code == 200

    def test_list_files_returns_file_array(self, client, sample_integration_files):
        """Test list files returns files array."""
        response = client.get("/api/v1/files")
        data = response.json()

        assert "files" in data
        assert isinstance(data["files"], list)

    def test_list_files_includes_count(self, client, sample_integration_files):
        """Test list files includes count."""
        response = client.get("/api/v1/files")
        data = response.json()

        assert "count" in data
        assert data["count"] == 2

    def test_list_files_includes_backend(self, client, sample_integration_files):
        """Test list files includes backend."""
        response = client.get("/api/v1/files")
        data = response.json()

        assert "backend" in data


class TestGetFileMetadataEndpoint:
    """Test suite for get file metadata endpoint."""

    def test_get_metadata_returns_200(self, client, sample_integration_files):
        """Test get metadata endpoint returns 200 OK."""
        response = client.get("/api/v1/files/file1.pdf")

        assert response.status_code == 200

    def test_get_metadata_includes_filename(self, client, sample_integration_files):
        """Test metadata response includes filename."""
        response = client.get("/api/v1/files/file1.pdf")
        data = response.json()

        assert "filename" in data
        assert data["filename"] == "file1.pdf"

    def test_get_metadata_includes_size(self, client, sample_integration_files):
        """Test metadata response includes size."""
        response = client.get("/api/v1/files/file1.pdf")
        data = response.json()

        assert "file_size" in data

    def test_get_metadata_returns_404_for_missing_file(self, client):
        """Test metadata returns 404 for non-existent file."""
        response = client.get("/api/v1/files/missing.pdf")

        assert response.status_code == 404


class TestDeleteFileEndpoint:
    """Test suite for delete file endpoint."""

    def test_delete_file_returns_200(self, client, sample_integration_files):
        """Test delete file endpoint returns 200 OK."""
        response = client.delete("/api/v1/files/file1.pdf")

        assert response.status_code == 200

    def test_delete_file_returns_success(self, client, sample_integration_files):
        """Test delete returns success response."""
        response = client.delete("/api/v1/files/file1.pdf")
        data = response.json()

        assert data["success"] is True

    def test_delete_file_includes_filename(self, client, sample_integration_files):
        """Test delete response includes filename."""
        response = client.delete("/api/v1/files/file1.pdf")
        data = response.json()

        assert data["filename"] == "file1.pdf"

    def test_delete_file_returns_404_for_missing_file(self, client):
        """Test delete returns 404 for non-existent file."""
        response = client.delete("/api/v1/files/missing.pdf")

        assert response.status_code == 404
