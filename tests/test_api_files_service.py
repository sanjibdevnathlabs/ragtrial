"""
Tests for file management service.

Unit tests with mocked database - no real DB connections.
Following best practices for fast, isolated testing.

Test Coverage:
- File listing with mocked database
- File metadata retrieval with mocked database
- File deletion with mocked database
- Error handling with mocked database
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app.modules.files import FileManagementService
from app.modules.file.entity import File
from app.modules.files.response import FileListResponse, FileMetadataResponse
from config import Config
from storage_backend.base import StorageProtocol


@pytest.fixture
def mock_db_file_service():
    """Mock database file service."""
    service = MagicMock()
    
    # Get current timestamp as integer (milliseconds)
    current_timestamp = int(datetime.now().timestamp() * 1000)
    
    # Mock file dictionaries (DBFileService returns dicts, not entities)
    file1_dict = {
        "id": "id1",
        "filename": "file1.pdf",
        "file_path": "source_docs/uuid1.pdf",
        "file_type": "pdf",  # Added file_type
        "file_size": 1024,
        "checksum": "checksum1",
        "storage_backend": "local",
        "indexed": False,
        "created_at": current_timestamp,  # Integer timestamp
        "updated_at": current_timestamp   # Integer timestamp
    }
    
    file2_dict = {
        "id": "id2",
        "filename": "file2.txt",
        "file_path": "source_docs/uuid2.txt",
        "file_type": "txt",  # Added file_type
        "file_size": 2048,
        "checksum": "checksum2",
        "storage_backend": "local",
        "indexed": False,
        "created_at": current_timestamp,  # Integer timestamp
        "updated_at": current_timestamp   # Integer timestamp
    }
    
    # Configure mock methods to match DBFileService interface
    service.list_all_files.return_value = [file1_dict, file2_dict]  # Returns list of dicts
    service.get_file_by_filename.side_effect = lambda fn: file1_dict if fn == "file1.pdf" else (file2_dict if fn == "file2.txt" else None)
    service.delete_file.return_value = None
    
    return service


@pytest.fixture
def config():
    """Get test config."""
    return Config()


@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    storage = Mock(spec=StorageProtocol)
    storage.delete_file.return_value = None
    return storage


@pytest.fixture
def service(config, mock_storage, mock_db_file_service):
    """Create file service instance with mocked dependencies."""
    # Mock SessionFactory to prevent database connections
    with patch("database.session.SessionFactory") as mock_sf_class:
        mock_sf = MagicMock()
        mock_sf_class.return_value = mock_sf
        
        # Mock FileService where it's USED (in files/service.py), not where it's defined
        with patch("app.modules.files.service.DBFileService", return_value=mock_db_file_service):
            service = FileManagementService(config, mock_storage)
            yield service


class TestListFiles:
    """Test suite for file listing."""
    
    def test_list_files_returns_response(self, service):
        """Test list returns FileListResponse."""
        result = service.list_files()
        
        assert isinstance(result, FileListResponse)
    
    def test_list_files_includes_all_files(self, service):
        """Test list includes all files from database."""
        result = service.list_files()
        
        assert result.count == 2
        filenames = [f["filename"] for f in result.files]
        assert "file1.pdf" in filenames
        assert "file2.txt" in filenames
    
    def test_list_files_includes_count(self, service):
        """Test list includes file count."""
        result = service.list_files()
        
        assert result.count == 2
    
    def test_list_files_includes_backend(self, service):
        """Test list includes storage backend."""
        result = service.list_files()
        
        assert result.backend == "local"
    
    def test_list_files_returns_empty_list(self, config, mock_storage):
        """Test list handles empty database."""
        mock_empty_db = MagicMock()
        mock_empty_db.list_all_files.return_value = []  # Fixed method name
        
        with patch("database.session.SessionFactory"):
            with patch("app.modules.files.service.DBFileService", return_value=mock_empty_db):
                service = FileManagementService(config, mock_storage)
                result = service.list_files()
        
        assert result.files == []
        assert result.count == 0


class TestGetFileMetadata:
    """Test suite for file metadata retrieval."""
    
    def test_get_file_metadata_returns_response(self, service):
        """Test get metadata returns FileMetadataResponse."""
        result = service.get_file_metadata("file1.pdf")
        
        assert isinstance(result, FileMetadataResponse)
    
    def test_get_file_metadata_includes_filename(self, service):
        """Test metadata includes filename."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.filename == "file1.pdf"
    
    def test_get_file_metadata_includes_size(self, service):
        """Test metadata includes file size."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.file_size == 1024
    
    def test_get_file_metadata_includes_file_type(self, service):
        """Test metadata includes file type."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.file_type == "pdf"
    
    def test_get_file_metadata_raises_for_missing_file(self, service):
        """Test metadata raises for non-existent file."""
        with pytest.raises(FileNotFoundError):
            service.get_file_metadata("missing.pdf")
    
    def test_get_file_metadata_includes_path(self, service):
        """Test metadata includes file path."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.file_path == "source_docs/uuid1.pdf"
    
    def test_get_file_metadata_includes_checksum(self, service):
        """Test metadata includes checksum."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.checksum.startswith("checksum1")
    
    def test_get_file_metadata_includes_indexed_status(self, service):
        """Test metadata includes indexed status."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.indexed is False


class TestDeleteFile:
    """Test suite for file deletion."""
    
    def test_delete_file_returns_success(self, service, mock_storage):
        """Test delete returns success response."""
        result = service.delete_file("file1.pdf")
        
        assert result["success"] is True
    
    def test_delete_file_includes_filename(self, service, mock_storage):
        """Test delete response includes filename."""
        result = service.delete_file("file1.pdf")
        
        assert result["filename"] == "file1.pdf"
    
    def test_delete_file_raises_for_missing_file(self, service):
        """Test delete raises for non-existent file."""
        with pytest.raises(FileNotFoundError):
            service.delete_file("missing.pdf")
    
    def test_delete_file_calls_storage(self, service, mock_storage):
        """Test delete calls storage backend."""
        service.delete_file("file1.pdf")
        
        # Storage delete should be called with the file path
        mock_storage.delete_file.assert_called_once()
    
    def test_delete_file_calls_database(self, service, mock_db_file_service, mock_storage):
        """Test delete calls database service."""
        service.delete_file("file1.pdf")
        
        # Database delete is called with file ID (not filename)
        mock_db_file_service.delete_file.assert_called_once_with("id1")
