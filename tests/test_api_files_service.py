"""
Tests for file management service.

Tests file listing, metadata, and deletion operations with database backend.
"""

import pytest
from unittest.mock import Mock
import time

from app.modules.files import FileManagementService
from app.modules.file.core import FileService as DBFileService
from app.modules.file.entity import File
from app.modules.files.response import FileListResponse, FileMetadataResponse
from config import Config
from storage_backend.base import StorageProtocol


@pytest.fixture
def db_file_service():
    """Get database file service."""
    return DBFileService()


@pytest.fixture
def sample_files(db_file_service):
    """Create sample files in database for testing."""
    files_data = [
        {
            "filename": "file1.pdf",
            "file_path": "source_docs/uuid1.pdf",
            "file_size": 1024,
            "checksum": "checksum1" + str(time.time()),
            "storage_backend": "local"
        },
        {
            "filename": "file2.txt",
            "file_path": "source_docs/uuid2.txt",
            "file_size": 2048,
            "checksum": "checksum2" + str(time.time()),
            "storage_backend": "local"
        }
    ]
    
    created_files = []
    for file_data in files_data:
        file_record = db_file_service.create_file_record(**file_data)
        created_files.append(file_record)
    
    return created_files


@pytest.fixture
def config():
    """Get real config."""
    return Config()


@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    storage = Mock(spec=StorageProtocol)
    storage.delete_file.return_value = None
    return storage


@pytest.fixture
def service(config, mock_storage):
    """Create file service instance with real database."""
    return FileManagementService(config, mock_storage)


class TestListFiles:
    """Test suite for file listing."""
    
    def test_list_files_returns_response(self, service):
        """Test list returns FileListResponse."""
        result = service.list_files()
        
        assert isinstance(result, FileListResponse)
    
    def test_list_files_includes_all_files(self, service, sample_files):
        """Test list includes all files from database."""
        result = service.list_files()
        
        assert result.count == 2
        filenames = [f["filename"] for f in result.files]
        assert "file1.pdf" in filenames
        assert "file2.txt" in filenames
    
    def test_list_files_includes_count(self, service, sample_files):
        """Test list includes file count."""
        result = service.list_files()
        
        assert result.count == 2
    
    def test_list_files_includes_backend(self, service):
        """Test list includes storage backend."""
        result = service.list_files()
        
        assert result.backend == "local"
    
    def test_list_files_returns_empty_list(self, service):
        """Test list handles empty database."""
        result = service.list_files()
        
        assert result.files == []
        assert result.count == 0


class TestGetFileMetadata:
    """Test suite for file metadata retrieval."""
    
    def test_get_file_metadata_returns_response(self, service, sample_files):
        """Test get metadata returns FileMetadataResponse."""
        result = service.get_file_metadata("file1.pdf")
        
        assert isinstance(result, FileMetadataResponse)
    
    def test_get_file_metadata_includes_filename(self, service, sample_files):
        """Test metadata includes filename."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.filename == "file1.pdf"
    
    def test_get_file_metadata_includes_size(self, service, sample_files):
        """Test metadata includes file size."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.file_size == 1024
    
    def test_get_file_metadata_includes_file_type(self, service, sample_files):
        """Test metadata includes file type."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.file_type == "pdf"
    
    def test_get_file_metadata_raises_for_missing_file(self, service):
        """Test metadata raises for non-existent file."""
        with pytest.raises(FileNotFoundError):
            service.get_file_metadata("missing.pdf")
    
    def test_get_file_metadata_includes_path(self, service, sample_files):
        """Test metadata includes file path."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.file_path == "source_docs/uuid1.pdf"
    
    def test_get_file_metadata_includes_checksum(self, service, sample_files):
        """Test metadata includes checksum."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.checksum.startswith("checksum1")
    
    def test_get_file_metadata_includes_indexed_status(self, service, sample_files):
        """Test metadata includes indexed status."""
        result = service.get_file_metadata("file1.pdf")
        
        assert result.indexed is False


class TestDeleteFile:
    """Test suite for file deletion."""
    
    def test_delete_file_returns_success(self, service, sample_files, mock_storage):
        """Test delete returns success response."""
        result = service.delete_file("file1.pdf")
        
        assert result["success"] is True
    
    def test_delete_file_includes_filename(self, service, sample_files, mock_storage):
        """Test delete response includes filename."""
        result = service.delete_file("file1.pdf")
        
        assert result["filename"] == "file1.pdf"
    
    def test_delete_file_raises_for_missing_file(self, service):
        """Test delete raises for non-existent file."""
        with pytest.raises(FileNotFoundError):
            service.delete_file("missing.pdf")
    
    def test_delete_file_calls_storage(self, service, sample_files, mock_storage):
        """Test delete calls storage backend."""
        service.delete_file("file1.pdf")
        
        # Storage delete should be called with the file path
        mock_storage.delete_file.assert_called_once()
    
    def test_delete_file_soft_deletes_in_database(self, service, sample_files, db_file_service, mock_storage):
        """Test delete soft-deletes record in database."""
        service.delete_file("file1.pdf")
        
        # File should not be found after deletion (soft delete)
        file_data = db_file_service.get_file_by_filename("file1.pdf")
        assert file_data is None
