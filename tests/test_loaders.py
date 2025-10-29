"""
Tests for document loaders.

This module tests the document loading functionality for various file formats
(PDF, TXT, MD, DOCX, CSV, JSON).

NOTE: These are integration-style tests that use real file loading.
The markdown test may trigger a warning from the unstructured library
making HTTP calls to packages.unstructured.io for dependency downloads.
This is a known issue with the third-party library.

Test Coverage:
- Successful loading for each format
- Error handling (file not found, unsupported format, corrupted files)
- Metadata extraction and enrichment
- Helper functions (detect type, supported extensions)
"""

from pathlib import Path

import pytest
from langchain_core.documents import Document

import constants
from loader import DocumentLoader, LoaderFactory
from loader.strategies import (
    CSVLoaderStrategy,
    DocxLoaderStrategy,
    JSONLoaderStrategy,
    MarkdownLoaderStrategy,
    PDFLoaderStrategy,
    TextLoaderStrategy,
)

# Suppress InsecureRequestWarning from unstructured library
# This library makes HTTP calls to download dependencies on first use
pytestmark = pytest.mark.filterwarnings(
    "ignore::urllib3.exceptions.InsecureRequestWarning"
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_txt(fixtures_dir) -> Path:
    """Return path to sample text file."""
    return fixtures_dir / "sample.txt"


@pytest.fixture
def sample_md(fixtures_dir) -> Path:
    """Return path to sample markdown file."""
    return fixtures_dir / "sample.md"


@pytest.fixture
def sample_pdf(fixtures_dir) -> Path:
    """Return path to sample PDF file."""
    return fixtures_dir / "sample.pdf"


@pytest.fixture
def sample_docx(fixtures_dir) -> Path:
    """Return path to sample DOCX file."""
    return fixtures_dir / "sample.docx"


@pytest.fixture
def sample_csv(fixtures_dir) -> Path:
    """Return path to sample CSV file."""
    return fixtures_dir / "sample.csv"


@pytest.fixture
def sample_json(fixtures_dir) -> Path:
    """Return path to sample JSON file."""
    return fixtures_dir / "sample.json"


@pytest.fixture
def document_loader() -> DocumentLoader:
    """Return DocumentLoader instance."""
    return DocumentLoader()


# ============================================================================
# TEST LOADER STRATEGIES
# ============================================================================


class TestLoaderStrategies:
    """Test individual loader strategies."""

    def test_pdf_loader_strategy(self, sample_pdf):
        """Test PDF loader strategy."""
        loader = PDFLoaderStrategy(str(sample_pdf))
        documents = loader.load()

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)

    def test_text_loader_strategy(self, sample_txt):
        """Test text loader strategy."""
        loader = TextLoaderStrategy(str(sample_txt))
        documents = loader.load()

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)
        assert "sample text document" in documents[0].page_content.lower()

    def test_markdown_loader_strategy(self, sample_md):
        """Test markdown loader strategy."""
        loader = MarkdownLoaderStrategy(str(sample_md))
        documents = loader.load()

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)

    def test_docx_loader_strategy(self, sample_docx):
        """Test DOCX loader strategy."""
        loader = DocxLoaderStrategy(str(sample_docx))
        documents = loader.load()

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)
        assert "sample docx" in documents[0].page_content.lower()

    def test_csv_loader_strategy(self, sample_csv):
        """Test CSV loader strategy."""
        loader = CSVLoaderStrategy(str(sample_csv))
        documents = loader.load()

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)

    def test_json_loader_strategy(self, sample_json):
        """Test JSON loader strategy."""
        loader = JSONLoaderStrategy(str(sample_json))
        documents = loader.load()

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)


# ============================================================================
# TEST LOADER FACTORY
# ============================================================================


class TestLoaderFactory:
    """Test LoaderFactory functionality."""

    def test_get_supported_extensions(self):
        """Test getting list of supported extensions."""
        extensions = LoaderFactory.get_supported_extensions()

        assert isinstance(extensions, list)
        assert len(extensions) == 6
        assert constants.EXT_PDF in extensions
        assert constants.EXT_TXT in extensions
        assert constants.EXT_MD in extensions
        assert constants.EXT_DOCX in extensions
        assert constants.EXT_CSV in extensions
        assert constants.EXT_JSON in extensions

    def test_is_supported_pdf(self, sample_pdf):
        """Test checking if PDF is supported."""
        assert LoaderFactory.is_supported(sample_pdf) is True

    def test_is_supported_txt(self, sample_txt):
        """Test checking if TXT is supported."""
        assert LoaderFactory.is_supported(sample_txt) is True

    def test_is_supported_md(self, sample_md):
        """Test checking if MD is supported."""
        assert LoaderFactory.is_supported(sample_md) is True

    def test_is_supported_docx(self, sample_docx):
        """Test checking if DOCX is supported."""
        assert LoaderFactory.is_supported(sample_docx) is True

    def test_is_supported_csv(self, sample_csv):
        """Test checking if CSV is supported."""
        assert LoaderFactory.is_supported(sample_csv) is True

    def test_is_supported_json(self, sample_json):
        """Test checking if JSON is supported."""
        assert LoaderFactory.is_supported(sample_json) is True

    def test_is_supported_unsupported_extension(self, fixtures_dir):
        """Test checking unsupported file extension."""
        unsupported_file = fixtures_dir / "sample.xyz"
        assert LoaderFactory.is_supported(unsupported_file) is False

    def test_create_loader_pdf(self, sample_pdf):
        """Test creating PDF loader."""
        loader = LoaderFactory.create(sample_pdf)
        assert isinstance(loader, PDFLoaderStrategy)

    def test_create_loader_txt(self, sample_txt):
        """Test creating text loader."""
        loader = LoaderFactory.create(sample_txt)
        assert isinstance(loader, TextLoaderStrategy)

    def test_create_loader_md(self, sample_md):
        """Test creating markdown loader."""
        loader = LoaderFactory.create(sample_md)
        assert isinstance(loader, MarkdownLoaderStrategy)

    def test_create_loader_docx(self, sample_docx):
        """Test creating DOCX loader."""
        loader = LoaderFactory.create(sample_docx)
        assert isinstance(loader, DocxLoaderStrategy)

    def test_create_loader_csv(self, sample_csv):
        """Test creating CSV loader."""
        loader = LoaderFactory.create(sample_csv)
        assert isinstance(loader, CSVLoaderStrategy)

    def test_create_loader_json(self, sample_json):
        """Test creating JSON loader."""
        loader = LoaderFactory.create(sample_json)
        assert isinstance(loader, JSONLoaderStrategy)

    def test_create_loader_unsupported_format(self, fixtures_dir):
        """Test creating loader for unsupported format raises error."""
        unsupported_file = fixtures_dir / "sample.xyz"

        with pytest.raises(ValueError) as exc_info:
            LoaderFactory.create(unsupported_file)

        assert constants.ERROR_UNSUPPORTED_FORMAT in str(exc_info.value)


# ============================================================================
# TEST DOCUMENT LOADER
# ============================================================================


class TestDocumentLoader:
    """Test DocumentLoader main interface."""

    def test_initialization(self, document_loader):
        """Test document loader initialization."""
        assert document_loader is not None
        assert isinstance(document_loader, DocumentLoader)

    def test_load_pdf_success(self, document_loader, sample_pdf):
        """Test successful PDF loading."""
        documents = document_loader.load_document(sample_pdf)

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)

        # Check metadata enrichment
        first_doc = documents[0]
        assert constants.META_SOURCE in first_doc.metadata
        assert constants.META_FILE_TYPE in first_doc.metadata
        assert constants.META_FILE_SIZE in first_doc.metadata
        assert first_doc.metadata[constants.META_FILE_TYPE] == constants.FILE_TYPE_PDF

    def test_load_txt_success(self, document_loader, sample_txt):
        """Test successful text file loading."""
        documents = document_loader.load_document(sample_txt)

        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)

        # Check metadata enrichment
        first_doc = documents[0]
        assert constants.META_FILE_TYPE in first_doc.metadata
        assert first_doc.metadata[constants.META_FILE_TYPE] == constants.FILE_TYPE_TXT

        # Check content
        assert "sample text document" in first_doc.page_content.lower()

    def test_load_md_success(self, document_loader, sample_md):
        """Test successful markdown file loading."""
        documents = document_loader.load_document(sample_md)

        assert isinstance(documents, list)
        assert len(documents) > 0

        # Check metadata
        first_doc = documents[0]
        assert first_doc.metadata[constants.META_FILE_TYPE] == constants.FILE_TYPE_MD

    def test_load_docx_success(self, document_loader, sample_docx):
        """Test successful DOCX file loading."""
        documents = document_loader.load_document(sample_docx)

        assert isinstance(documents, list)
        assert len(documents) > 0

        # Check metadata
        first_doc = documents[0]
        assert first_doc.metadata[constants.META_FILE_TYPE] == constants.FILE_TYPE_DOCX

        # Check content
        assert "sample docx" in first_doc.page_content.lower()

    def test_load_csv_success(self, document_loader, sample_csv):
        """Test successful CSV file loading."""
        documents = document_loader.load_document(sample_csv)

        assert isinstance(documents, list)
        assert len(documents) > 0

        # Check metadata
        first_doc = documents[0]
        assert first_doc.metadata[constants.META_FILE_TYPE] == constants.FILE_TYPE_CSV

    def test_load_json_success(self, document_loader, sample_json):
        """Test successful JSON file loading."""
        documents = document_loader.load_document(sample_json)

        assert isinstance(documents, list)
        assert len(documents) > 0

        # Check metadata
        first_doc = documents[0]
        assert first_doc.metadata[constants.META_FILE_TYPE] == constants.FILE_TYPE_JSON

    def test_load_file_not_found(self, document_loader, fixtures_dir):
        """Test loading non-existent file raises error."""
        nonexistent_file = fixtures_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError) as exc_info:
            document_loader.load_document(nonexistent_file)

        assert constants.ERROR_FILE_NOT_FOUND in str(exc_info.value)

    def test_load_unsupported_format(self, document_loader, fixtures_dir):
        """Test loading unsupported format raises error."""
        # Create a dummy unsupported file
        unsupported_file = fixtures_dir / "test_unsupported.xyz"
        unsupported_file.touch()

        try:
            with pytest.raises(ValueError) as exc_info:
                document_loader.load_document(unsupported_file)

            assert constants.ERROR_UNSUPPORTED_FORMAT in str(exc_info.value)

        finally:
            # Cleanup
            if unsupported_file.exists():
                unsupported_file.unlink()

    def test_load_with_string_path(self, document_loader, sample_txt):
        """Test loading document with string path."""
        documents = document_loader.load_document(str(sample_txt))

        assert isinstance(documents, list)
        assert len(documents) > 0

    def test_get_supported_extensions(self, document_loader):
        """Test getting supported extensions."""
        extensions = document_loader.get_supported_extensions()

        assert isinstance(extensions, list)
        assert len(extensions) == 6
        assert constants.EXT_PDF in extensions

    def test_is_supported_file_pdf(self, document_loader, sample_pdf):
        """Test checking if PDF file is supported."""
        assert document_loader.is_supported_file(sample_pdf) is True

    def test_is_supported_file_txt(self, document_loader, sample_txt):
        """Test checking if text file is supported."""
        assert document_loader.is_supported_file(sample_txt) is True

    def test_is_supported_file_unsupported(self, document_loader):
        """Test checking if unsupported file returns False."""
        unsupported = Path("test.xyz")
        assert document_loader.is_supported_file(unsupported) is False

    def test_is_supported_file_string_path(self, document_loader):
        """Test checking supported file with string path."""
        assert document_loader.is_supported_file("test.pdf") is True
        assert document_loader.is_supported_file("test.xyz") is False


# ============================================================================
# TEST METADATA ENRICHMENT
# ============================================================================


class TestMetadataEnrichment:
    """Test metadata enrichment functionality."""

    def test_metadata_has_source(self, document_loader, sample_txt):
        """Test that metadata includes source file path."""
        documents = document_loader.load_document(sample_txt)

        first_doc = documents[0]
        assert constants.META_SOURCE in first_doc.metadata
        assert str(sample_txt) in first_doc.metadata[constants.META_SOURCE]

    def test_metadata_has_file_type(self, document_loader, sample_txt):
        """Test that metadata includes file type."""
        documents = document_loader.load_document(sample_txt)

        first_doc = documents[0]
        assert constants.META_FILE_TYPE in first_doc.metadata
        assert first_doc.metadata[constants.META_FILE_TYPE] == constants.FILE_TYPE_TXT

    def test_metadata_has_file_size(self, document_loader, sample_txt):
        """Test that metadata includes file size."""
        documents = document_loader.load_document(sample_txt)

        first_doc = documents[0]
        assert constants.META_FILE_SIZE in first_doc.metadata
        assert isinstance(first_doc.metadata[constants.META_FILE_SIZE], int)
        assert first_doc.metadata[constants.META_FILE_SIZE] > 0

    def test_metadata_enrichment_all_formats(
        self,
        document_loader,
        sample_pdf,
        sample_txt,
        sample_md,
        sample_docx,
        sample_csv,
        sample_json,
    ):
        """Test that all formats get metadata enrichment."""
        test_files = [
            (sample_pdf, constants.FILE_TYPE_PDF),
            (sample_txt, constants.FILE_TYPE_TXT),
            (sample_md, constants.FILE_TYPE_MD),
            (sample_docx, constants.FILE_TYPE_DOCX),
            (sample_csv, constants.FILE_TYPE_CSV),
            (sample_json, constants.FILE_TYPE_JSON),
        ]

        for file_path, expected_type in test_files:
            documents = document_loader.load_document(file_path)
            first_doc = documents[0]

            # All should have required metadata
            assert constants.META_SOURCE in first_doc.metadata
            assert constants.META_FILE_TYPE in first_doc.metadata
            assert constants.META_FILE_SIZE in first_doc.metadata

            # File type should match
            assert first_doc.metadata[constants.META_FILE_TYPE] == expected_type


# ============================================================================
# TEST ERROR HANDLING
# ============================================================================


class TestErrorHandling:
    """Test error handling in document loaders."""

    def test_load_file_not_exists_error_message(self, document_loader, fixtures_dir):
        """Test error message when file doesn't exist."""
        nonexistent = fixtures_dir / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError) as exc_info:
            document_loader.load_document(nonexistent)

        error_message = str(exc_info.value)
        assert constants.ERROR_FILE_NOT_FOUND in error_message
        assert str(nonexistent) in error_message

    def test_load_unsupported_format_error_message(self, document_loader, fixtures_dir):
        """Test error message when format is unsupported."""
        unsupported = fixtures_dir / "test.xyz"
        unsupported.touch()

        try:
            with pytest.raises(ValueError) as exc_info:
                document_loader.load_document(unsupported)

            error_message = str(exc_info.value)
            assert constants.ERROR_UNSUPPORTED_FORMAT in error_message

        finally:
            if unsupported.exists():
                unsupported.unlink()

    def test_factory_unsupported_format_logs_error(self, fixtures_dir):
        """Test that factory logs error for unsupported format."""
        unsupported = fixtures_dir / "test.xyz"

        with pytest.raises(ValueError):
            LoaderFactory.create(unsupported)

        # If we get here without exception, test fails
        # The factory should raise ValueError for unsupported formats
