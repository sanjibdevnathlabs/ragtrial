"""
Tests for upload service.

Tests file upload business logic.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from app.modules.upload import UploadService
from app.api.models import UploadResponse
from config import Config
from storage_backend.base import StorageProtocol


@pytest.fixture
def mock_config():
    """Mock configuration."""
    config = Mock()
    config.storage = Mock()
    config.storage.backend = "local"
    config.storage.max_file_size_mb = 100
    config.storage.allowed_extensions = [".pdf", ".txt", ".md"]
    return config


@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    storage = Mock(spec=StorageProtocol)
    storage.upload_file.return_value = "source_docs/test.pdf"
    return storage


@pytest.fixture
def service(mock_config, mock_storage):
    """Create upload service instance."""
    return UploadService(mock_config, mock_storage)


class TestUploadFile:
    """Test suite for file upload."""
    
    def test_upload_file_success(self, service, mock_storage):
        """Test successful file upload."""
        content = b"test content"
        
        result = service.upload_file("test.pdf", content)
        
        assert isinstance(result, UploadResponse)
        assert result.success is True
        assert result.filename == "test.pdf"
        assert result.size == len(content)
    
    def test_upload_file_calls_storage(self, service, mock_storage):
        """Test upload calls storage backend."""
        content = b"test content"
        
        service.upload_file("test.pdf", content)
        
        mock_storage.upload_file.assert_called_once_with("test.pdf", content)
    
    def test_upload_file_returns_correct_path(self, service, mock_storage):
        """Test upload returns storage path."""
        content = b"test content"
        mock_storage.upload_file.return_value = "custom/path/file.pdf"
        
        result = service.upload_file("test.pdf", content)
        
        assert result.path == "custom/path/file.pdf"
    
    def test_upload_file_rejects_empty_filename(self, service):
        """Test upload fails for empty filename."""
        content = b"test content"
        
        with pytest.raises(ValueError):
            service.upload_file("", content)
    
    def test_upload_file_rejects_invalid_extension(self, service):
        """Test upload fails for invalid extension."""
        content = b"test content"
        
        with pytest.raises(ValueError):
            service.upload_file("virus.exe", content)
    
    def test_upload_file_rejects_oversized_file(self, service):
        """Test upload fails for oversized file."""
        content = b"x" * (101 * 1024 * 1024)
        
        with pytest.raises(ValueError):
            service.upload_file("large.pdf", content)
    
    def test_upload_file_propagates_storage_error(self, service, mock_storage):
        """Test upload propagates storage errors."""
        content = b"test content"
        mock_storage.upload_file.side_effect = Exception("Storage failed")
        
        with pytest.raises(Exception) as exc_info:
            service.upload_file("test.pdf", content)
        
        assert "Storage failed" in str(exc_info.value)
    
    def test_upload_file_accepts_all_allowed_extensions(self, service):
        """Test upload accepts all configured extensions."""
        content = b"test content"
        filenames = ["doc.pdf", "notes.txt", "readme.md"]
        
        for filename in filenames:
            result = service.upload_file(filename, content)
            assert result.success is True


class TestValidateFile:
    """Test suite for file validation."""
    
    def test_validate_file_calls_all_validators(self, service):
        """Test validation calls all validator methods."""
        content = b"test content"
        
        service._validate_file("test.pdf", content)
        
        # No exception means all validators passed
    
    def test_validate_file_fails_on_filename(self, service):
        """Test validation fails for invalid filename."""
        content = b"test content"
        
        with pytest.raises(ValueError):
            service._validate_file("", content)
    
    def test_validate_file_fails_on_extension(self, service):
        """Test validation fails for invalid extension."""
        content = b"test content"
        
        with pytest.raises(ValueError):
            service._validate_file("file.exe", content)
    
    def test_validate_file_fails_on_size(self, service):
        """Test validation fails for invalid size."""
        content = b"x" * (101 * 1024 * 1024)
        
        with pytest.raises(ValueError):
            service._validate_file("test.pdf", content)


class TestStoreFile:
    """Test suite for file storage."""
    
    def test_store_file_returns_path(self, service, mock_storage):
        """Test store returns file path."""
        content = b"test content"
        mock_storage.upload_file.return_value = "path/to/file.pdf"
        
        path = service._store_file("test.pdf", content)
        
        assert path == "path/to/file.pdf"
    
    def test_store_file_calls_storage(self, service, mock_storage):
        """Test store calls storage backend."""
        content = b"test content"
        
        service._store_file("test.pdf", content)
        
        mock_storage.upload_file.assert_called_once()
    
    def test_store_file_propagates_exception(self, service, mock_storage):
        """Test store propagates storage exceptions."""
        content = b"test content"
        mock_storage.upload_file.side_effect = IOError("Disk full")
        
        with pytest.raises(IOError):
            service._store_file("test.pdf", content)

