"""
Integration tests for API endpoints.

Tests full request/response flow with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.api.main import app


@pytest.fixture
def mock_storage():
    """Mock storage backend for integration tests."""
    storage = Mock()
    storage.upload_file.return_value = "source_docs/test.pdf"
    storage.list_files.return_value = ["file1.pdf", "file2.txt"]
    storage.file_exists.return_value = True
    storage.get_file_metadata.return_value = {
        "filename": "test.pdf",
        "size": 1024,
        "modified_time": "2025-10-28T00:00:00",
        "path": "source_docs/test.pdf"
    }
    return storage


@pytest.fixture
def client(mock_storage):
    """Create test client with mocked storage."""
    with patch("app.api.dependencies.create_storage", return_value=mock_storage):
        yield TestClient(app)


class TestHealthEndpoint:
    """Test suite for health endpoint."""
    
    def test_health_returns_200(self, client):
        """Test health endpoint returns 200 OK."""
        response = client.get("/health")
        
        assert response.status_code == 200
    
    def test_health_returns_json(self, client):
        """Test health endpoint returns JSON."""
        response = client.get("/health")
        
        assert response.headers["content-type"] == "application/json"
    
    def test_health_includes_status(self, client):
        """Test health response includes status."""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_includes_storage_backend(self, client):
        """Test health response includes storage backend."""
        response = client.get("/health")
        data = response.json()
        
        assert "storage_backend" in data
    
    def test_health_includes_version(self, client):
        """Test health response includes version."""
        response = client.get("/health")
        data = response.json()
        
        assert "version" in data


class TestUploadEndpoint:
    """Test suite for upload endpoint."""
    
    def test_upload_returns_200(self, client, mock_storage):
        """Test upload endpoint returns 200 OK."""
        files = {"file": ("test.pdf", b"test content", "application/pdf")}
        
        response = client.post("/api/v1/upload", files=files)
        
        assert response.status_code == 200
    
    def test_upload_returns_success_response(self, client, mock_storage):
        """Test upload returns success response."""
        files = {"file": ("test.pdf", b"test content", "application/pdf")}
        
        response = client.post("/api/v1/upload", files=files)
        data = response.json()
        
        assert data["success"] is True
    
    def test_upload_includes_filename(self, client, mock_storage):
        """Test upload response includes filename."""
        files = {"file": ("test.pdf", b"test content", "application/pdf")}
        
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
    
    def test_list_files_returns_200(self, client):
        """Test list files endpoint returns 200 OK."""
        response = client.get("/api/v1/files")
        
        assert response.status_code == 200
    
    def test_list_files_returns_file_array(self, client):
        """Test list files returns files array."""
        response = client.get("/api/v1/files")
        data = response.json()
        
        assert "files" in data
        assert isinstance(data["files"], list)
    
    def test_list_files_includes_count(self, client):
        """Test list files includes count."""
        response = client.get("/api/v1/files")
        data = response.json()
        
        assert "count" in data
        assert data["count"] == 2
    
    def test_list_files_includes_backend(self, client):
        """Test list files includes backend."""
        response = client.get("/api/v1/files")
        data = response.json()
        
        assert "backend" in data


class TestGetFileMetadataEndpoint:
    """Test suite for get file metadata endpoint."""
    
    def test_get_metadata_returns_200(self, client):
        """Test get metadata endpoint returns 200 OK."""
        response = client.get("/api/v1/files/test.pdf")
        
        assert response.status_code == 200
    
    def test_get_metadata_includes_filename(self, client):
        """Test metadata response includes filename."""
        response = client.get("/api/v1/files/test.pdf")
        data = response.json()
        
        assert "filename" in data
    
    def test_get_metadata_includes_size(self, client):
        """Test metadata response includes size."""
        response = client.get("/api/v1/files/test.pdf")
        data = response.json()
        
        assert "size" in data
    
    def test_get_metadata_returns_404_for_missing_file(self, client, mock_storage):
        """Test metadata returns 404 for non-existent file."""
        mock_storage.file_exists.return_value = False
        
        response = client.get("/api/v1/files/missing.pdf")
        
        assert response.status_code == 404


class TestDeleteFileEndpoint:
    """Test suite for delete file endpoint."""
    
    def test_delete_file_returns_200(self, client):
        """Test delete file endpoint returns 200 OK."""
        response = client.delete("/api/v1/files/test.pdf")
        
        assert response.status_code == 200
    
    def test_delete_file_returns_success(self, client):
        """Test delete returns success response."""
        response = client.delete("/api/v1/files/test.pdf")
        data = response.json()
        
        assert data["success"] is True
    
    def test_delete_file_includes_filename(self, client):
        """Test delete response includes filename."""
        response = client.delete("/api/v1/files/test.pdf")
        data = response.json()
        
        assert data["filename"] == "test.pdf"
    
    def test_delete_file_returns_404_for_missing_file(self, client, mock_storage):
        """Test delete returns 404 for non-existent file."""
        mock_storage.file_exists.return_value = False
        
        response = client.delete("/api/v1/files/missing.pdf")
        
        assert response.status_code == 404

