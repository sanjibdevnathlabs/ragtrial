"""
Tests for S3 Storage Backend.

Unit tests with FULL MOCKING - no actual S3 operations.
Mocks boto3 Session and Client for isolated testing.
"""

import pytest
from io import BytesIO
from unittest.mock import Mock, MagicMock, patch
from botocore.exceptions import ClientError, NoCredentialsError

from config import Config
from storage_backend.implementations.s3 import S3Storage


@pytest.fixture
def mock_config():
    """Create test config."""
    return Config()


@pytest.fixture
def mock_boto3_session():
    """Create mock boto3 Session."""
    session = MagicMock()
    credentials = MagicMock()
    credentials.method = "iam-role"
    session.get_credentials.return_value = credentials
    return session


@pytest.fixture
def mock_s3_client():
    """Create mock S3 client."""
    client = MagicMock()
    
    # Mock head_bucket (bucket access verification)
    client.head_bucket.return_value = {}
    
    # Mock upload_fileobj
    client.upload_fileobj.return_value = None
    
    # Mock download_fileobj
    def mock_download(bucket, key, stream):
        stream.write(b"Test content from S3")
    client.download_fileobj.side_effect = mock_download
    
    # Mock head_object (file exists check)
    client.head_object.return_value = {
        "ContentLength": 100,
        "LastModified": "2025-10-27T00:00:00Z",
        "ETag": '"abc123"'
    }
    
    # Mock delete_object
    client.delete_object.return_value = {}
    
    # Mock list_objects_v2 (paginator)
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {"Contents": [{"Key": "file1.txt"}, {"Key": "file2.pdf"}]}
    ]
    client.get_paginator.return_value = paginator
    
    return client


@pytest.fixture
def s3_storage(mock_config, mock_boto3_session, mock_s3_client):
    """Create S3Storage with mocked boto3."""
    with patch("boto3.Session", return_value=mock_boto3_session):
        mock_boto3_session.client.return_value = mock_s3_client
        storage = S3Storage(mock_config)
        return storage


class TestS3StorageInitialization:
    """Test S3Storage initialization."""
    
    def test_initialization_with_credential_chain(self, mock_config, mock_boto3_session, mock_s3_client):
        """Test initialization uses credential chain by default."""
        with patch("boto3.Session", return_value=mock_boto3_session) as mock_session:
            mock_boto3_session.client.return_value = mock_s3_client
            
            storage = S3Storage(mock_config)
            
            assert storage.bucket_name == "test-rag-documents"
            assert storage.region == "us-east-1"
            mock_session.assert_called_once()
    
    def test_initialization_verifies_bucket_access(self, mock_config, mock_boto3_session, mock_s3_client):
        """Test initialization verifies bucket access."""
        with patch("boto3.Session", return_value=mock_boto3_session):
            mock_boto3_session.client.return_value = mock_s3_client
            
            storage = S3Storage(mock_config)
            
            mock_s3_client.head_bucket.assert_called_once_with(Bucket="test-rag-documents")


class TestS3StorageUpload:
    """Test file upload operations."""
    
    def test_upload_file_success(self, s3_storage, mock_s3_client):
        """Test successful file upload."""
        file_content = b"Test document content"
        file_stream = BytesIO(file_content)
        filename = "test.txt"
        
        result = s3_storage.upload_file(file_stream, filename)
        
        assert result == filename
        mock_s3_client.upload_fileobj.assert_called_once()


class TestS3StorageDownload:
    """Test file download operations."""
    
    def test_download_existing_file(self, s3_storage, mock_s3_client):
        """Test downloading existing file."""
        filename = "test.txt"
        
        result = s3_storage.download_file(filename)
        
        assert isinstance(result, BytesIO)
        assert result.read() == b"Test content from S3"
        mock_s3_client.download_fileobj.assert_called_once()
    
    def test_download_nonexistent_file_raises_error(self, s3_storage, mock_s3_client):
        """Test downloading non-existent file raises FileNotFoundError."""
        # Mock head_object to raise 404
        mock_s3_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}},
            "head_object"
        )
        
        with pytest.raises(FileNotFoundError) as exc_info:
            s3_storage.download_file("nonexistent.txt")
        
        assert "File not found in storage" in str(exc_info.value)


class TestS3StorageDelete:
    """Test file deletion operations."""
    
    def test_delete_existing_file(self, s3_storage, mock_s3_client):
        """Test deleting existing file."""
        filename = "test.txt"
        
        result = s3_storage.delete_file(filename)
        
        assert result is True
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-rag-documents",
            Key=filename
        )
    
    def test_delete_nonexistent_file_returns_false(self, s3_storage, mock_s3_client):
        """Test deleting non-existent file returns False."""
        # Mock head_object to indicate file doesn't exist
        mock_s3_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}},
            "head_object"
        )
        
        result = s3_storage.delete_file("nonexistent.txt")
        
        assert result is False


class TestS3StorageList:
    """Test file listing operations."""
    
    def test_list_all_files(self, s3_storage, mock_s3_client):
        """Test listing all files."""
        files = s3_storage.list_files()
        
        assert len(files) == 2
        assert "file1.txt" in files
        assert "file2.pdf" in files
        mock_s3_client.get_paginator.assert_called_once_with("list_objects_v2")
    
    def test_list_files_with_prefix(self, s3_storage, mock_s3_client):
        """Test listing files with prefix."""
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Contents": [{"Key": "docs/file1.txt"}]}
        ]
        mock_s3_client.get_paginator.return_value = paginator
        
        files = s3_storage.list_files(prefix="docs/")
        
        assert "docs/file1.txt" in files
    
    def test_list_files_empty_bucket(self, s3_storage, mock_s3_client):
        """Test listing files in empty bucket."""
        paginator = MagicMock()
        paginator.paginate.return_value = [{}]  # No Contents key
        mock_s3_client.get_paginator.return_value = paginator
        
        files = s3_storage.list_files()
        
        assert files == []


class TestS3StorageFileExists:
    """Test file existence checks."""
    
    def test_file_exists_returns_true(self, s3_storage, mock_s3_client):
        """Test file_exists returns True for existing file."""
        mock_s3_client.head_object.return_value = {}
        
        assert s3_storage.file_exists("test.txt") is True
    
    def test_file_exists_returns_false(self, s3_storage, mock_s3_client):
        """Test file_exists returns False for non-existent file."""
        mock_s3_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}},
            "head_object"
        )
        
        assert s3_storage.file_exists("nonexistent.txt") is False


class TestS3StorageMetadata:
    """Test file metadata operations."""
    
    def test_get_file_metadata_success(self, s3_storage, mock_s3_client):
        """Test getting metadata for existing file."""
        from datetime import datetime
        
        mock_s3_client.head_object.return_value = {
            "ContentLength": 12345,
            "LastModified": datetime(2025, 10, 27),
            "ETag": '"abc123"'
        }
        
        metadata = s3_storage.get_file_metadata("test.txt")
        
        assert metadata["filename"] == "test.txt"
        assert metadata["size"] == "12345"
        assert "modified_time" in metadata
        assert metadata["etag"] == "abc123"
    
    def test_get_metadata_nonexistent_file_raises_error(self, s3_storage, mock_s3_client):
        """Test getting metadata for non-existent file raises error."""
        mock_s3_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}},
            "head_object"
        )
        
        with pytest.raises(FileNotFoundError) as exc_info:
            s3_storage.get_file_metadata("nonexistent.txt")
        
        assert "File not found in storage" in str(exc_info.value)


class TestS3CredentialDiscovery:
    """Test credential discovery mechanisms."""
    
    def test_credential_chain_no_explicit_credentials(self, mock_config):
        """Test credential chain is used when use_explicit_credentials is False."""
        mock_config.storage.s3.use_explicit_credentials = False
        
        with patch("boto3.Session") as mock_session:
            mock_boto_session = MagicMock()
            mock_client = MagicMock()
            mock_client.head_bucket.return_value = {}
            mock_boto_session.client.return_value = mock_client
            mock_session.return_value = mock_boto_session
            
            storage = S3Storage(mock_config)
            
            # Verify Session created with only region (credential chain)
            mock_session.assert_called_once_with(region_name="us-east-1")
    
    def test_localstack_explicit_credentials(self, mock_config):
        """Test LocalStack uses explicit credentials."""
        mock_config.storage.s3.use_localstack = True
        mock_config.storage.s3.use_explicit_credentials = True
        mock_config.storage.s3.endpoint_url = "http://localhost:4566"
        
        with patch("boto3.Session") as mock_session:
            mock_boto_session = MagicMock()
            mock_client = MagicMock()
            mock_client.head_bucket.return_value = {}
            mock_boto_session.client.return_value = mock_client
            mock_session.return_value = mock_boto_session
            
            storage = S3Storage(mock_config)
            
            # Verify Session created with test credentials
            call_kwargs = mock_session.call_args[1]
            assert call_kwargs["aws_access_key_id"] == "test"
            assert call_kwargs["aws_secret_access_key"] == "test"


class TestS3StorageIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_workflow(self, s3_storage, mock_s3_client):
        """Test complete file lifecycle."""
        filename = "workflow_test.txt"
        content = b"Test workflow content"
        
        # Upload
        result = s3_storage.upload_file(BytesIO(content), filename)
        assert result == filename
        
        # Check existence
        mock_s3_client.head_object.return_value = {}
        assert s3_storage.file_exists(filename) is True
        
        # Get metadata
        from datetime import datetime
        mock_s3_client.head_object.return_value = {
            "ContentLength": len(content),
            "LastModified": datetime.now(),
            "ETag": '"test123"'
        }
        metadata = s3_storage.get_file_metadata(filename)
        assert metadata["filename"] == filename
        
        # Delete
        assert s3_storage.delete_file(filename) is True

