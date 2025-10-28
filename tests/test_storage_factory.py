"""
Tests for Storage Factory.

Unit tests for storage backend factory pattern.
"""

import pytest
from unittest.mock import patch

from config import Config
from storage_backend.factory import create_storage, get_supported_backends
from storage_backend.implementations.local import LocalStorage
from storage_backend.implementations.s3 import S3Storage


@pytest.fixture
def mock_config():
    """Create test config."""
    return Config()


class TestStorageFactory:
    """Test storage factory creation."""
    
    def test_create_local_storage(self, mock_config, tmp_path):
        """Test creating local storage backend."""
        mock_config.storage.backend = "local"
        mock_config.storage.local.path = str(tmp_path)
        
        storage = create_storage(mock_config)
        
        assert isinstance(storage, LocalStorage)
        assert hasattr(storage, "upload_file")
        assert hasattr(storage, "download_file")
        assert hasattr(storage, "delete_file")
        assert hasattr(storage, "list_files")
        assert hasattr(storage, "file_exists")
        assert hasattr(storage, "get_file_metadata")
    
    def test_create_s3_storage(self, mock_config):
        """Test creating S3 storage backend."""
        mock_config.storage.backend = "s3"
        
        with patch("boto3.Session"):
            with patch("storage_backend.implementations.s3.S3Storage._verify_bucket_access"):
                storage = create_storage(mock_config)
                
                assert isinstance(storage, S3Storage)
                assert hasattr(storage, "upload_file")
                assert hasattr(storage, "download_file")
    
    def test_invalid_backend_raises_error(self, mock_config):
        """Test that invalid backend raises ValueError."""
        mock_config.storage.backend = "invalid_backend"
        
        with pytest.raises(ValueError) as exc_info:
            create_storage(mock_config)
        
        assert "Invalid storage backend" in str(exc_info.value)
        assert "invalid_backend" in str(exc_info.value)


class TestSupportedBackends:
    """Test supported backends listing."""
    
    def test_get_supported_backends(self):
        """Test getting list of supported backends."""
        backends = get_supported_backends()
        
        assert isinstance(backends, list)
        assert "local" in backends
        assert "s3" in backends
        assert len(backends) == 2


class TestStorageProtocol:
    """Test that all backends implement the protocol."""
    
    def test_local_storage_implements_protocol(self, mock_config, tmp_path):
        """Test LocalStorage implements all protocol methods."""
        mock_config.storage.backend = "local"
        mock_config.storage.local.path = str(tmp_path)
        
        storage = create_storage(mock_config)
        
        # Check all protocol methods exist and are callable
        assert callable(storage.upload_file)
        assert callable(storage.download_file)
        assert callable(storage.delete_file)
        assert callable(storage.list_files)
        assert callable(storage.file_exists)
        assert callable(storage.get_file_metadata)
    
    def test_s3_storage_implements_protocol(self, mock_config):
        """Test S3Storage implements all protocol methods."""
        mock_config.storage.backend = "s3"
        
        with patch("boto3.Session"):
            with patch("storage_backend.implementations.s3.S3Storage._verify_bucket_access"):
                storage = create_storage(mock_config)
                
                # Check all protocol methods exist and are callable
                assert callable(storage.upload_file)
                assert callable(storage.download_file)
                assert callable(storage.delete_file)
                assert callable(storage.list_files)
                assert callable(storage.file_exists)
                assert callable(storage.get_file_metadata)

