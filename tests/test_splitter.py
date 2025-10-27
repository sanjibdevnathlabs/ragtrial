"""
Tests for document splitters.

This module tests the text splitting functionality including:
- Token-based splitting
- Factory pattern implementation
- Parameter validation
- Chunk overlap preservation

Test Coverage:
- Successful splitting with various parameters
- Error handling (invalid parameters, empty documents)
- Metadata preservation in chunks
- Factory methods and supported types
"""

import pytest
from langchain_core.documents import Document

import constants
from splitter import DocumentSplitter, SplitterFactory
from splitter.strategies import TokenSplitterStrategy


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_document():
    """Return a sample document with enough text to split."""
    text = " ".join([f"This is sentence {i}." for i in range(100)])
    return Document(
        page_content=text,
        metadata={"source": "test.txt", "file_type": "text"}
    )


@pytest.fixture
def sample_documents():
    """Return multiple sample documents."""
    docs = []
    for i in range(3):
        text = " ".join([f"Document {i} sentence {j}." for j in range(50)])
        docs.append(Document(
            page_content=text,
            metadata={"source": f"test{i}.txt", "file_type": "text"}
        ))
    return docs


@pytest.fixture
def short_document():
    """Return a short document that won't be split."""
    return Document(
        page_content="This is a short text.",
        metadata={"source": "short.txt"}
    )


@pytest.fixture
def document_splitter():
    """Return DocumentSplitter with default parameters."""
    return DocumentSplitter()


# ============================================================================
# TEST SPLITTER STRATEGY
# ============================================================================


class TestTokenSplitterStrategy:
    """Test TokenSplitterStrategy directly."""

    def test_initialization_default_params(self):
        """Test initialization with default parameters."""
        splitter = TokenSplitterStrategy()

        assert splitter.chunk_size == 512
        assert splitter.chunk_overlap == 100

    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        splitter = TokenSplitterStrategy(chunk_size=1000, chunk_overlap=200)

        assert splitter.chunk_size == 1000
        assert splitter.chunk_overlap == 200

    def test_split_documents_success(self, sample_document):
        """Test successful document splitting."""
        splitter = TokenSplitterStrategy(chunk_size=50, chunk_overlap=10)
        documents = [sample_document]

        chunks = splitter.split_documents(documents)

        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should split into multiple chunks
        assert all(isinstance(chunk, Document) for chunk in chunks)

    def test_split_preserves_metadata(self, sample_document):
        """Test that splitting preserves document metadata."""
        splitter = TokenSplitterStrategy(chunk_size=50, chunk_overlap=10)
        documents = [sample_document]

        chunks = splitter.split_documents(documents)

        # All chunks should preserve original metadata
        for chunk in chunks:
            assert chunk.metadata["source"] == sample_document.metadata["source"]
            assert chunk.metadata["file_type"] == sample_document.metadata["file_type"]

    def test_split_short_document(self, short_document):
        """Test splitting a document shorter than chunk size."""
        splitter = TokenSplitterStrategy(chunk_size=512, chunk_overlap=100)
        documents = [short_document]

        chunks = splitter.split_documents(documents)

        # Should return single chunk (document is too short to split)
        assert len(chunks) == 1
        assert chunks[0].page_content == short_document.page_content


# ============================================================================
# TEST SPLITTER FACTORY
# ============================================================================


class TestSplitterFactory:
    """Test SplitterFactory functionality."""

    def test_get_supported_types(self):
        """Test getting list of supported splitter types."""
        types = SplitterFactory.get_supported_types()

        assert isinstance(types, list)
        assert len(types) >= 1
        assert constants.SPLITTER_TYPE_TOKEN in types

    def test_is_supported_token(self):
        """Test checking if token splitter is supported."""
        assert SplitterFactory.is_supported(constants.SPLITTER_TYPE_TOKEN) is True

    def test_is_supported_unsupported_type(self):
        """Test checking unsupported splitter type."""
        assert SplitterFactory.is_supported("unsupported_type") is False

    def test_create_token_splitter_default(self):
        """Test creating token splitter with default parameters."""
        splitter = SplitterFactory.create()

        assert isinstance(splitter, TokenSplitterStrategy)
        assert splitter.chunk_size == constants.DEFAULT_CHUNK_SIZE
        assert splitter.chunk_overlap == constants.DEFAULT_CHUNK_OVERLAP

    def test_create_token_splitter_custom_params(self):
        """Test creating token splitter with custom parameters."""
        splitter = SplitterFactory.create(
            chunk_size=1000,
            chunk_overlap=200
        )

        assert isinstance(splitter, TokenSplitterStrategy)
        assert splitter.chunk_size == 1000
        assert splitter.chunk_overlap == 200

    def test_create_invalid_chunk_size(self):
        """Test creating splitter with invalid chunk size raises error."""
        with pytest.raises(ValueError) as exc_info:
            SplitterFactory.create(chunk_size=0)

        assert constants.ERROR_INVALID_CHUNK_SIZE in str(exc_info.value)

    def test_create_negative_chunk_size(self):
        """Test creating splitter with negative chunk size raises error."""
        with pytest.raises(ValueError) as exc_info:
            SplitterFactory.create(chunk_size=-100)

        assert constants.ERROR_INVALID_CHUNK_SIZE in str(exc_info.value)

    def test_create_invalid_overlap(self):
        """Test creating splitter with invalid overlap raises error."""
        with pytest.raises(ValueError) as exc_info:
            SplitterFactory.create(chunk_size=100, chunk_overlap=-10)

        assert constants.ERROR_INVALID_OVERLAP in str(exc_info.value)

    def test_create_overlap_greater_than_chunk_size(self):
        """Test creating splitter with overlap >= chunk_size raises error."""
        with pytest.raises(ValueError) as exc_info:
            SplitterFactory.create(chunk_size=100, chunk_overlap=100)

        assert constants.ERROR_INVALID_OVERLAP in str(exc_info.value)

    def test_create_unsupported_type(self):
        """Test creating unsupported splitter type raises error."""
        with pytest.raises(ValueError) as exc_info:
            SplitterFactory.create(splitter_type="unsupported_type")

        assert "Unsupported splitter type" in str(exc_info.value)


# ============================================================================
# TEST DOCUMENT SPLITTER
# ============================================================================


class TestDocumentSplitter:
    """Test DocumentSplitter main interface."""

    def test_initialization_default_params(self):
        """Test initialization with default parameters."""
        splitter = DocumentSplitter()

        assert splitter.chunk_size == constants.DEFAULT_CHUNK_SIZE
        assert splitter.chunk_overlap == constants.DEFAULT_CHUNK_OVERLAP
        assert splitter.splitter_type == constants.SPLITTER_TYPE_TOKEN

    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        splitter = DocumentSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            splitter_type=constants.SPLITTER_TYPE_TOKEN
        )

        assert splitter.chunk_size == 1000
        assert splitter.chunk_overlap == 200
        assert splitter.splitter_type == constants.SPLITTER_TYPE_TOKEN

    def test_split_documents_success(self, sample_documents):
        """Test successful document splitting."""
        # Use smaller chunk size to ensure splitting happens
        splitter = DocumentSplitter(chunk_size=50, chunk_overlap=10)
        chunks = splitter.split_documents(sample_documents)

        assert isinstance(chunks, list)
        assert len(chunks) > len(sample_documents)  # Should split into more chunks
        assert all(isinstance(chunk, Document) for chunk in chunks)

    def test_split_single_document(self, document_splitter, sample_document):
        """Test splitting single document."""
        chunks = document_splitter.split_documents([sample_document])

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        assert all(isinstance(chunk, Document) for chunk in chunks)

    def test_split_preserves_metadata(self, document_splitter, sample_document):
        """Test that metadata is preserved in chunks."""
        chunks = document_splitter.split_documents([sample_document])

        for chunk in chunks:
            assert "source" in chunk.metadata
            assert "file_type" in chunk.metadata
            assert chunk.metadata["source"] == sample_document.metadata["source"]

    def test_split_empty_list_raises_error(self, document_splitter):
        """Test splitting empty document list raises error."""
        with pytest.raises(ValueError) as exc_info:
            document_splitter.split_documents([])

        assert constants.ERROR_EMPTY_TEXT in str(exc_info.value)

    def test_split_with_small_chunk_size(self, sample_document):
        """Test splitting with small chunk size creates more chunks."""
        splitter = DocumentSplitter(chunk_size=50, chunk_overlap=10)

        chunks = splitter.split_documents([sample_document])

        assert len(chunks) > 5  # Small chunks = more pieces

    def test_split_with_large_chunk_size(self, sample_document):
        """Test splitting with large chunk size creates fewer chunks."""
        splitter = DocumentSplitter(chunk_size=5000, chunk_overlap=100)

        chunks = splitter.split_documents([sample_document])

        # Large chunk size might not split at all
        assert len(chunks) >= 1

    def test_get_chunk_size(self, document_splitter):
        """Test getting configured chunk size."""
        assert document_splitter.get_chunk_size() == constants.DEFAULT_CHUNK_SIZE

    def test_get_chunk_overlap(self, document_splitter):
        """Test getting configured chunk overlap."""
        assert document_splitter.get_chunk_overlap() == constants.DEFAULT_CHUNK_OVERLAP

    def test_get_splitter_type(self, document_splitter):
        """Test getting configured splitter type."""
        assert document_splitter.get_splitter_type() == constants.SPLITTER_TYPE_TOKEN


# ============================================================================
# TEST EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_split_document_with_no_metadata(self):
        """Test splitting document with no metadata."""
        doc = Document(page_content="This is a test document with no metadata.")
        splitter = DocumentSplitter()

        chunks = splitter.split_documents([doc])

        assert len(chunks) >= 1
        assert all(isinstance(chunk, Document) for chunk in chunks)

    def test_split_document_with_empty_content(self):
        """Test splitting document with empty content."""
        doc = Document(page_content="", metadata={"source": "empty.txt"})
        splitter = DocumentSplitter()

        # Should handle gracefully (might return empty or single chunk)
        chunks = splitter.split_documents([doc])

        assert isinstance(chunks, list)

    def test_split_with_minimal_overlap(self):
        """Test splitting with minimal overlap (0)."""
        splitter = DocumentSplitter(chunk_size=100, chunk_overlap=0)
        doc = Document(page_content=" ".join([f"Word{i}" for i in range(200)]))

        chunks = splitter.split_documents([doc])

        assert len(chunks) >= 1

    def test_split_with_maximum_overlap(self):
        """Test splitting with maximum valid overlap (chunk_size - 1)."""
        chunk_size = 100
        splitter = DocumentSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_size - 1
        )
        doc = Document(page_content=" ".join([f"Word{i}" for i in range(200)]))

        chunks = splitter.split_documents([doc])

        assert len(chunks) >= 1


# ============================================================================
# TEST INTEGRATION
# ============================================================================


class TestIntegration:
    """Test integration scenarios."""

    def test_load_and_split_workflow(self, sample_documents):
        """Test typical load → split workflow."""
        # Simulate documents coming from loader
        documents = sample_documents

        # Split documents
        splitter = DocumentSplitter(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_documents(documents)

        # Verify workflow
        assert len(chunks) > len(documents)
        assert all(isinstance(chunk, Document) for chunk in chunks)
        assert all(chunk.metadata for chunk in chunks)

    def test_multiple_split_operations(self, sample_document):
        """Test multiple split operations with same splitter."""
        splitter = DocumentSplitter(chunk_size=100, chunk_overlap=20)

        # First split
        chunks1 = splitter.split_documents([sample_document])

        # Second split (should be consistent)
        chunks2 = splitter.split_documents([sample_document])

        assert len(chunks1) == len(chunks2)

    def test_different_splitters_same_document(self, sample_document):
        """Test different splitters on same document."""
        splitter1 = DocumentSplitter(chunk_size=100, chunk_overlap=20)
        splitter2 = DocumentSplitter(chunk_size=200, chunk_overlap=40)

        chunks1 = splitter1.split_documents([sample_document])
        chunks2 = splitter2.split_documents([sample_document])

        # Smaller chunks = more pieces
        assert len(chunks1) > len(chunks2)

