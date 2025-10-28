"""
Tests for file management service.

Tests file listing, metadata, and deletion operations.
"""

import pytest
from unittest.mock import Mock

from api.modules.files import FileService
from api.models import FileListResponse, FileMetadataResponse
from config import Config
from storage_backend.base import StorageProtocol


@pytest.fixture
def mock_config():
    """Mock configuration."""
    config = Mock()
    config.storage = Mock()
    config.storage.backend = "local"
    return config


@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    storage = Mock(spec=StorageProtocol)
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
def service(mock_config, mock_storage):
    """Create file service instance."""
    return FileService(mock_config, mock_storage)


class TestListFiles:
    """Test suite for file listing."""
    
    def test_list_files_returns_response(self, service):
        """Test list returns FileListResponse."""
        result = service.list_files()
        
        assert isinstance(result, FileListResponse)
    
    def test_list_files_includes_all_files(self, service, mock_storage):
        """Test list includes all files from storage."""
        result = service.list_files()
        
        assert len(result.files) == 2
        assert "file1.pdf" in result.files
        assert "file2.txt" in result.files
    
    def test_list_files_includes_count(self, service):
        """Test list includes file count."""
        result = service.list_files()
        
        assert result.count == 2
    
    def test_list_files_includes_backend(self, service):
        """Test list includes storage backend."""
        result = service.list_files()
        
        assert result.backend == "local"
    
    def test_list_files_calls_storage(self, service, mock_storage):
        """Test list calls storage backend."""
        service.list_files()
        
        mock_storage.list_files.assert_called_once()
    
    def test_list_files_returns_empty_list(self, service, mock_storage):
        """Test list handles empty storage."""
        mock_storage.list_files.return_value = []
        
        result = service.list_files()
        
        assert result.files == []
        assert result.count == 0


class TestGetFileMetadata:
    """Test suite for file metadata retrieval."""
    
    def test_get_file_metadata_returns_response(self, service):
        """Test get metadata returns FileMetadataResponse."""
        result = service.get_file_metadata("test.pdf")
        
        assert isinstance(result, FileMetadataResponse)
    
    def test_get_file_metadata_includes_filename(self, service):
        """Test metadata includes filename."""
        result = service.get_file_metadata("test.pdf")
        
        assert result.filename == "test.pdf"
    
    def test_get_file_metadata_includes_size(self, service):
        """Test metadata includes file size."""
        result = service.get_file_metadata("test.pdf")
        
        assert result.size == "1024"
    
    def test_get_file_metadata_includes_modified_time(self, service):
        """Test metadata includes modified time."""
        result = service.get_file_metadata("test.pdf")
        
        assert result.modified_time == "2025-10-28T00:00:00"
    
    def test_get_file_metadata_checks_existence(self, service, mock_storage):
        """Test metadata checks if file exists."""
        service.get_file_metadata("test.pdf")
        
        mock_storage.file_exists.assert_called_once_with("test.pdf")
    
    def test_get_file_metadata_raises_for_missing_file(self, service, mock_storage):
        """Test metadata raises for non-existent file."""
        mock_storage.file_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            service.get_file_metadata("missing.pdf")
    
    def test_get_file_metadata_calls_storage(self, service, mock_storage):
        """Test metadata calls storage backend."""
        service.get_file_metadata("test.pdf")
        
        mock_storage.get_file_metadata.assert_called_once_with("test.pdf")
    
    def test_get_file_metadata_includes_path(self, service):
        """Test metadata includes file path."""
        result = service.get_file_metadata("test.pdf")
        
        assert result.path == "source_docs/test.pdf"


class TestDeleteFile:
    """Test suite for file deletion."""
    
    def test_delete_file_returns_success(self, service):
        """Test delete returns success response."""
        result = service.delete_file("test.pdf")
        
        assert result["success"] is True
    
    def test_delete_file_includes_filename(self, service):
        """Test delete response includes filename."""
        result = service.delete_file("test.pdf")
        
        assert result["filename"] == "test.pdf"
    
    def test_delete_file_checks_existence(self, service, mock_storage):
        """Test delete checks if file exists."""
        service.delete_file("test.pdf")
        
        mock_storage.file_exists.assert_called_once_with("test.pdf")
    
    def test_delete_file_raises_for_missing_file(self, service, mock_storage):
        """Test delete raises for non-existent file."""
        mock_storage.file_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            service.delete_file("missing.pdf")
    
    def test_delete_file_calls_storage(self, service, mock_storage):
        """Test delete calls storage backend."""
        service.delete_file("test.pdf")
        
        mock_storage.delete_file.assert_called_once_with("test.pdf")
    
    def test_delete_file_propagates_storage_error(self, service, mock_storage):
        """Test delete propagates storage errors."""
        mock_storage.delete_file.side_effect = IOError("Permission denied")
        
        with pytest.raises(IOError):
            service.delete_file("test.pdf")


class TestGetMetadata:
    """Test suite for internal metadata retrieval."""
    
    def test_get_metadata_returns_dict(self, service, mock_storage):
        """Test _get_metadata returns dictionary."""
        result = service._get_metadata("test.pdf")
        
        assert isinstance(result, dict)
    
    def test_get_metadata_calls_storage(self, service, mock_storage):
        """Test _get_metadata calls storage."""
        service._get_metadata("test.pdf")
        
        mock_storage.get_file_metadata.assert_called_once()
    
    def test_get_metadata_propagates_exception(self, service, mock_storage):
        """Test _get_metadata propagates exceptions."""
        mock_storage.get_file_metadata.side_effect = Exception("API error")
        
        with pytest.raises(Exception):
            service._get_metadata("test.pdf")

