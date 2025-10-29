"""
Tests for Local Storage Backend.

Unit tests with proper mocking - no actual file system operations on source_docs.
Uses temporary test directory for isolation.
"""

from io import BytesIO

import pytest

from config import Config
from storage_backend.implementations.local import LocalStorage


@pytest.fixture
def mock_config():
    """Create test config."""
    return Config()


@pytest.fixture
def temp_storage_path(tmp_path):
    """Create temporary storage directory."""
    storage_dir = tmp_path / "test_storage"
    storage_dir.mkdir()
    return storage_dir


@pytest.fixture
def local_storage(mock_config, temp_storage_path):
    """Create LocalStorage with temporary path."""
    mock_config.storage.local.path = str(temp_storage_path)
    return LocalStorage(mock_config)


class TestLocalStorageInitialization:
    """Test LocalStorage initialization."""

    def test_initialization_creates_directory(self, mock_config, tmp_path):
        """Test that initialization creates storage directory."""
        storage_path = tmp_path / "new_storage"
        mock_config.storage.local.path = str(storage_path)

        assert not storage_path.exists()

        storage = LocalStorage(mock_config)

        assert storage_path.exists()
        assert storage.storage_path == storage_path

    def test_initialization_uses_existing_directory(
        self, mock_config, temp_storage_path
    ):
        """Test initialization with existing directory."""
        mock_config.storage.local.path = str(temp_storage_path)
        storage = LocalStorage(mock_config)

        assert storage.storage_path == temp_storage_path


class TestLocalStorageUpload:
    """Test file upload operations."""

    def test_upload_file_success(self, local_storage):
        """Test successful file upload."""
        file_content = b"Test document content"
        file_stream = BytesIO(file_content)
        filename = "test.txt"

        result = local_storage.upload_file(file_stream, filename)

        assert filename in result
        assert (local_storage.storage_path / filename).exists()
        assert (local_storage.storage_path / filename).read_bytes() == file_content

    def test_upload_overwrites_existing_file(self, local_storage):
        """Test that upload overwrites existing file."""
        filename = "test.txt"

        # Upload first version
        original_content = b"Original content"
        local_storage.upload_file(BytesIO(original_content), filename)

        # Upload new version
        new_content = b"New content"
        local_storage.upload_file(BytesIO(new_content), filename)

        # Verify new content
        assert (local_storage.storage_path / filename).read_bytes() == new_content


class TestLocalStorageDownload:
    """Test file download operations."""

    def test_download_existing_file(self, local_storage):
        """Test downloading existing file."""
        filename = "test.txt"
        content = b"Test content"

        # Upload file first
        local_storage.upload_file(BytesIO(content), filename)

        # Download file
        result = local_storage.download_file(filename)

        assert isinstance(result, BytesIO)
        assert result.read() == content

    def test_download_nonexistent_file_raises_error(self, local_storage):
        """Test downloading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as exc_info:
            local_storage.download_file("nonexistent.txt")

        assert "File not found in storage" in str(exc_info.value)


class TestLocalStorageDelete:
    """Test file deletion operations."""

    def test_delete_existing_file(self, local_storage):
        """Test deleting existing file."""
        filename = "test.txt"

        # Upload file first
        local_storage.upload_file(BytesIO(b"content"), filename)
        assert (local_storage.storage_path / filename).exists()

        # Delete file
        result = local_storage.delete_file(filename)

        assert result is True
        assert not (local_storage.storage_path / filename).exists()

    def test_delete_nonexistent_file_returns_false(self, local_storage):
        """Test deleting non-existent file returns False."""
        result = local_storage.delete_file("nonexistent.txt")

        assert result is False


class TestLocalStorageList:
    """Test file listing operations."""

    def test_list_files_empty_directory(self, local_storage):
        """Test listing files in empty directory."""
        files = local_storage.list_files()

        assert files == []

    def test_list_all_files(self, local_storage):
        """Test listing all files."""
        # Upload multiple files
        local_storage.upload_file(BytesIO(b"content1"), "file1.txt")
        local_storage.upload_file(BytesIO(b"content2"), "file2.pdf")
        local_storage.upload_file(BytesIO(b"content3"), "file3.md")

        files = local_storage.list_files()

        assert len(files) == 3
        assert "file1.txt" in files
        assert "file2.pdf" in files
        assert "file3.md" in files

    def test_list_files_with_prefix(self, local_storage):
        """Test listing files with prefix filter."""
        # Upload files with different prefixes
        local_storage.upload_file(BytesIO(b"content"), "doc1.txt")
        local_storage.upload_file(BytesIO(b"content"), "doc2.txt")
        local_storage.upload_file(BytesIO(b"content"), "report.pdf")

        files = local_storage.list_files(prefix="doc")

        assert len(files) == 2
        assert "doc1.txt" in files
        assert "doc2.txt" in files
        assert "report.pdf" not in files


class TestLocalStorageFileExists:
    """Test file existence checks."""

    def test_file_exists_returns_true(self, local_storage):
        """Test file_exists returns True for existing file."""
        filename = "test.txt"
        local_storage.upload_file(BytesIO(b"content"), filename)

        assert local_storage.file_exists(filename) is True

    def test_file_exists_returns_false(self, local_storage):
        """Test file_exists returns False for non-existent file."""
        assert local_storage.file_exists("nonexistent.txt") is False


class TestLocalStorageMetadata:
    """Test file metadata operations."""

    def test_get_file_metadata_success(self, local_storage):
        """Test getting metadata for existing file."""
        filename = "test.txt"
        content = b"Test content"
        local_storage.upload_file(BytesIO(content), filename)

        metadata = local_storage.get_file_metadata(filename)

        assert metadata["filename"] == filename
        assert metadata["size"] == str(len(content))
        assert "modified_time" in metadata
        assert "path" in metadata

    def test_get_metadata_nonexistent_file_raises_error(self, local_storage):
        """Test getting metadata for non-existent file raises error."""
        with pytest.raises(FileNotFoundError) as exc_info:
            local_storage.get_file_metadata("nonexistent.txt")

        assert "File not found in storage" in str(exc_info.value)


class TestLocalStorageIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow(self, local_storage):
        """Test complete file lifecycle."""
        filename = "workflow_test.txt"
        content = b"Test workflow content"

        # Upload
        upload_path = local_storage.upload_file(BytesIO(content), filename)
        assert filename in upload_path

        # Check existence
        assert local_storage.file_exists(filename) is True

        # List files
        files = local_storage.list_files()
        assert filename in files

        # Get metadata
        metadata = local_storage.get_file_metadata(filename)
        assert metadata["filename"] == filename

        # Download
        downloaded = local_storage.download_file(filename)
        assert downloaded.read() == content

        # Delete
        assert local_storage.delete_file(filename) is True
        assert local_storage.file_exists(filename) is False
