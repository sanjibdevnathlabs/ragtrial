"""
Tests for upload validators.

Tests file upload validation logic.
"""

from unittest.mock import Mock

import pytest

from app.modules.upload.validators import UploadValidator


@pytest.fixture
def mock_config():
    """Mock configuration with validation rules."""
    config = Mock()
    config.storage = Mock()
    config.storage.max_file_size_mb = 100
    config.storage.allowed_extensions = [
        ".pdf",
        ".txt",
        ".md",
        ".csv",
        ".docx",
        ".json",
    ]
    return config


@pytest.fixture
def validator(mock_config):
    """Create validator instance."""
    return UploadValidator(mock_config)


class TestValidateFilename:
    """Test suite for filename validation."""

    def test_validate_filename_accepts_valid_name(self, validator):
        """Test validation passes for valid filename."""
        validator.validate_filename("document.pdf")

    def test_validate_filename_rejects_empty_string(self, validator):
        """Test validation fails for empty filename."""
        with pytest.raises(ValueError) as exc_info:
            validator.validate_filename("")

        assert "Filename is required" in str(exc_info.value)

    def test_validate_filename_rejects_none(self, validator):
        """Test validation fails for None filename."""
        with pytest.raises(ValueError) as exc_info:
            validator.validate_filename(None)

        assert "Filename is required" in str(exc_info.value)


class TestValidateExtension:
    """Test suite for extension validation."""

    def test_validate_extension_accepts_pdf(self, validator):
        """Test validation passes for PDF files."""
        validator.validate_extension("document.pdf")

    def test_validate_extension_accepts_txt(self, validator):
        """Test validation passes for text files."""
        validator.validate_extension("notes.txt")

    def test_validate_extension_accepts_uppercase(self, validator):
        """Test validation accepts uppercase extensions."""
        validator.validate_extension("DOCUMENT.PDF")

    def test_validate_extension_rejects_exe(self, validator):
        """Test validation rejects executable files."""
        with pytest.raises(ValueError):
            validator.validate_extension("virus.exe")

    def test_validate_extension_rejects_no_extension(self, validator):
        """Test validation rejects files without extension."""
        with pytest.raises(ValueError):
            validator.validate_extension("document")

    def test_validate_extension_accepts_all_allowed_types(self, validator):
        """Test all allowed extensions pass validation."""
        filenames = [
            "doc.pdf",
            "notes.txt",
            "readme.md",
            "data.csv",
            "report.docx",
            "config.json",
        ]

        for filename in filenames:
            validator.validate_extension(filename)


class TestValidateSize:
    """Test suite for size validation."""

    def test_validate_size_accepts_small_file(self, validator):
        """Test validation passes for small files."""
        content = b"small content"
        validator.validate_size(content, "file.txt")

    def test_validate_size_accepts_exactly_max_size(self, validator):
        """Test validation passes for file at max size."""
        content = b"x" * (100 * 1024 * 1024)
        validator.validate_size(content, "file.txt")

    def test_validate_size_rejects_oversized_file(self, validator):
        """Test validation fails for oversized files."""
        content = b"x" * (101 * 1024 * 1024)

        with pytest.raises(ValueError):
            validator.validate_size(content, "large.pdf")

    def test_validate_size_accepts_empty_file(self, validator):
        """Test validation passes for empty files."""
        content = b""
        validator.validate_size(content, "empty.txt")

    def test_validate_size_rejects_double_max(self, validator):
        """Test validation fails for file double the max size."""
        content = b"x" * (200 * 1024 * 1024)

        with pytest.raises(ValueError):
            validator.validate_size(content, "huge.pdf")
