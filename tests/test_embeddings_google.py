"""
Tests for Google embeddings provider.

This module tests the Google embeddings implementation with mocked API calls.
Following unit testing best practices - no actual API calls.

Test Coverage:
- Initialization
- embed_documents() with batching
- embed_query() for single queries
- get_dimension()
- Error handling
- Batch processing logic
"""

from unittest.mock import patch

import pytest

from config import Config
from embeddings.implementations.google import GoogleEmbeddings

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_config():
    """Create mock configuration for testing (using test.toml)."""
    return Config()


@pytest.fixture
def google_embeddings(mock_config):
    """Create GoogleEmbeddings instance with mocked API."""
    with patch("google.generativeai.configure"):
        embeddings = GoogleEmbeddings(mock_config)
    return embeddings


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestGoogleEmbeddingsInitialization:
    """Test Google embeddings initialization."""

    def test_initialization_success(self, mock_config):
        """Test successful initialization."""
        with patch("google.generativeai.configure") as mock_configure:
            embeddings = GoogleEmbeddings(mock_config)

            assert embeddings.config is not None
            assert embeddings.model == mock_config.embeddings.google.model
            assert embeddings.dimension == mock_config.embeddings.dimension
            assert embeddings.task_type == mock_config.embeddings.google.task_type
            assert embeddings.batch_size == mock_config.embeddings.google.batch_size
            mock_configure.assert_called_once()

    def test_initialization_with_api_key(self, mock_config):
        """Test initialization configures API with key."""
        with patch("google.generativeai.configure") as mock_configure:
            GoogleEmbeddings(mock_config)
            mock_configure.assert_called_once_with(api_key=mock_config.google.api_key)


# ============================================================================
# EMBED DOCUMENTS TESTS
# ============================================================================


class TestEmbedDocuments:
    """Test embed_documents() method."""

    def test_embed_single_document(self, google_embeddings):
        """Test embedding a single document."""
        texts = ["Hello world"]
        expected_embeddings = [[0.1, 0.2, 0.3]]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.return_value = {"embedding": expected_embeddings}

            result = google_embeddings.embed_documents(texts)

            assert result == expected_embeddings
            mock_embed.assert_called_once()
            call_args = mock_embed.call_args
            assert call_args[1]["content"] == texts
            assert call_args[1]["model"] == google_embeddings.model

    def test_embed_multiple_documents(self, google_embeddings):
        """Test embedding multiple documents."""
        texts = ["Document 1", "Document 2", "Document 3"]
        expected_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.return_value = {"embedding": expected_embeddings}

            result = google_embeddings.embed_documents(texts)

            assert result == expected_embeddings
            assert len(result) == 3

    def test_embed_documents_batching(self, google_embeddings):
        """Test that documents are processed in batches."""
        # Set small batch size
        google_embeddings.batch_size = 2
        texts = ["Doc 1", "Doc 2", "Doc 3", "Doc 4", "Doc 5"]

        batch_embeddings = [[0.1, 0.2], [0.3, 0.4]]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.return_value = {"embedding": batch_embeddings}

            result = google_embeddings.embed_documents(texts)

            # Should be called 3 times (batches of 2, 2, 1)
            assert mock_embed.call_count == 3
            assert len(result) == 6  # 2 + 2 + 2 embeddings

    def test_embed_documents_empty_list(self, google_embeddings):
        """Test embedding empty list of documents."""
        texts = []

        with patch("google.generativeai.embed_content") as mock_embed:
            result = google_embeddings.embed_documents(texts)

            assert result == []
            mock_embed.assert_not_called()

    def test_embed_documents_error_handling(self, google_embeddings):
        """Test error handling in embed_documents."""
        texts = ["Test document"]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.side_effect = Exception("API Error")

            with pytest.raises(Exception) as exc_info:
                google_embeddings.embed_documents(texts)

            assert "API Error" in str(exc_info.value)


# ============================================================================
# EMBED QUERY TESTS
# ============================================================================


class TestEmbedQuery:
    """Test embed_query() method."""

    def test_embed_single_query(self, google_embeddings):
        """Test embedding a single query."""
        query = "What is machine learning?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.return_value = {"embedding": expected_embedding}

            result = google_embeddings.embed_query(query)

            assert result == expected_embedding
            mock_embed.assert_called_once()
            call_args = mock_embed.call_args
            assert call_args[1]["content"] == query
            assert call_args[1]["task_type"] == "retrieval_query"

    def test_embed_query_with_title(self, google_embeddings):
        """Test query embedding with title."""
        google_embeddings.title = "Test Title"
        query = "Test query"
        expected_embedding = [0.5, 0.6, 0.7]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.return_value = {"embedding": expected_embedding}

            result = google_embeddings.embed_query(query)

            assert result == expected_embedding
            call_args = mock_embed.call_args
            assert call_args[1]["title"] == "Test Title"

    def test_embed_query_error_handling(self, google_embeddings):
        """Test error handling in embed_query."""
        query = "Test query"

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.side_effect = ValueError("Invalid input")

            with pytest.raises(ValueError):
                google_embeddings.embed_query(query)


# ============================================================================
# GET DIMENSION TESTS
# ============================================================================


class TestGetDimension:
    """Test get_dimension() method."""

    def test_get_dimension_returns_config_value(self, google_embeddings):
        """Test get_dimension returns configured dimension."""
        result = google_embeddings.get_dimension()

        assert result == google_embeddings.dimension
        assert isinstance(result, int)
        assert result > 0

    def test_get_dimension_matches_config(self, mock_config):
        """Test dimension matches configuration."""
        with patch("google.generativeai.configure"):
            embeddings = GoogleEmbeddings(mock_config)

            assert embeddings.get_dimension() == mock_config.embeddings.dimension


# ============================================================================
# BATCH PROCESSING TESTS
# ============================================================================


class TestBatchProcessing:
    """Test internal batch processing logic."""

    def test_process_batch_success(self, google_embeddings):
        """Test successful batch processing."""
        batch = ["Text 1", "Text 2"]
        expected = [[0.1, 0.2], [0.3, 0.4]]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.return_value = {"embedding": expected}

            result = google_embeddings._process_batch(batch, batch_num=1)

            assert result == expected
            mock_embed.assert_called_once()

    def test_process_batch_handles_exceptions(self, google_embeddings):
        """Test batch processing error handling."""
        batch = ["Text 1"]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.side_effect = RuntimeError("Batch failed")

            with pytest.raises(RuntimeError):
                google_embeddings._process_batch(batch, batch_num=1)


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic usage scenarios with mocks."""

    def test_full_workflow(self, google_embeddings):
        """Test complete workflow from documents to embeddings."""
        documents = ["Doc 1", "Doc 2"]
        query = "Search query"

        doc_embeddings = [[0.1, 0.2], [0.3, 0.4]]
        query_embedding = [0.5, 0.6]

        with patch("google.generativeai.embed_content") as mock_embed:
            # First call for documents
            mock_embed.return_value = {"embedding": doc_embeddings}
            doc_result = google_embeddings.embed_documents(documents)

            # Second call for query
            mock_embed.return_value = {"embedding": query_embedding}
            query_result = google_embeddings.embed_query(query)

            assert doc_result == doc_embeddings
            assert query_result == query_embedding
            assert mock_embed.call_count == 2

    def test_large_document_set_batching(self, google_embeddings):
        """Test handling large number of documents with batching."""
        google_embeddings.batch_size = 10
        documents = [f"Document {i}" for i in range(50)]

        mock_embedding = [[0.1, 0.2] for _ in range(10)]

        with patch("google.generativeai.embed_content") as mock_embed:
            mock_embed.return_value = {"embedding": mock_embedding}

            result = google_embeddings.embed_documents(documents)

            # Should be called 5 times (50 docs / batch_size 10)
            assert mock_embed.call_count == 5
            # Total embeddings should be 50 (5 batches * 10 embeddings)
            assert len(result) == 50
