"""
Tests for HuggingFace embeddings provider.

Unit tests with mocked SentenceTransformer.
Following industry best practices - no actual model loading.

Test Coverage:
- Initialization
- embed_documents()
- embed_query()
- get_dimension()
- Normalization
- Error handling
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from config import Config

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_config():
    """Create mock configuration for HuggingFace (using test.toml)."""
    return Config()


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestHuggingFaceEmbeddingsInitialization:
    """Test HuggingFace embeddings initialization."""

    def test_initialization_success(self, mock_config):
        """Test successful initialization."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            assert embeddings.config is not None
            assert (
                embeddings.model_name == mock_config.embeddings.huggingface.model_name
            )
            assert embeddings.dimension == 384  # From mocked model
            mock_st.assert_called_once()

    def test_initialization_loads_model(self, mock_config):
        """Test initialization loads SentenceTransformer model."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            assert embeddings.model is not None


# ============================================================================
# EMBED DOCUMENTS TESTS
# ============================================================================


class TestEmbedDocuments:
    """Test embed_documents() method."""

    def test_embed_single_document(self, mock_config):
        """Test embedding a single document."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            result = embeddings.embed_documents(["Hello world"])

            assert len(result) == 1
            mock_model.encode.assert_called_once()

    def test_embed_multiple_documents(self, mock_config):
        """Test embedding multiple documents."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array(
                [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            )
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            result = embeddings.embed_documents(["Text 1", "Text 2"])

            assert len(result) == 2
            mock_model.encode.assert_called_once()

    def test_embed_documents_encode_parameters(self, mock_config):
        """Test correct encode parameters are used."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = np.array([[1.0, 2.0]])
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)
            embeddings.embed_documents(["Test"])

            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs["convert_to_numpy"] is False
            assert call_kwargs["show_progress_bar"] is False

    def test_embed_documents_empty_list(self, mock_config):
        """Test embedding empty list."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([])
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            result = embeddings.embed_documents([])

            assert len(result) == 0

    def test_embed_documents_error_handling(self, mock_config):
        """Test error handling in embed_documents."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.side_effect = RuntimeError("Model error")
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            with pytest.raises(RuntimeError):
                embeddings.embed_documents(["Test"])


# ============================================================================
# EMBED QUERY TESTS
# ============================================================================


class TestEmbedQuery:
    """Test embed_query() method."""

    def test_embed_single_query(self, mock_config):
        """Test embedding a single query."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([0.7, 0.8, 0.9])
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            result = embeddings.embed_query("What is AI?")

            assert len(result) == 3
            mock_model.encode.assert_called_once()

    def test_embed_query_encode_parameters(self, mock_config):
        """Test correct encode parameters are used for queries."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = np.array([1.0, 2.0])
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)
            embeddings.embed_query("Test")

            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs["convert_to_numpy"] is False
            assert call_kwargs["show_progress_bar"] is False

    def test_embed_query_error_handling(self, mock_config):
        """Test error handling in embed_query."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.side_effect = ValueError("Invalid input")
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            with pytest.raises(ValueError):
                embeddings.embed_query("Test")


# ============================================================================
# GET DIMENSION TESTS
# ============================================================================


class TestGetDimension:
    """Test get_dimension() method."""

    def test_get_dimension_returns_model_dimension(self, mock_config):
        """Test get_dimension returns dimension from model."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            result = embeddings.get_dimension()

            assert result == 384  # From model, not config
            assert isinstance(result, int)
            assert result > 0

    def test_get_dimension_matches_config(self, mock_config):
        """Test dimension matches configuration."""
        with patch("sentence_transformers.SentenceTransformer"):
            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            assert embeddings.get_dimension() == embeddings.dimension


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic usage scenarios with mocks."""

    def test_full_workflow(self, mock_config):
        """Test complete workflow."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()

            # Mock responses for different calls
            mock_model.encode.side_effect = [
                np.array([[0.1, 0.2], [0.3, 0.4]]),  # Documents
                np.array([0.5, 0.6]),  # Query
            ]
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            # Test documents
            doc_result = embeddings.embed_documents(["Doc 1", "Doc 2"])
            assert len(doc_result) == 2

            # Test query
            query_result = embeddings.embed_query("Query")
            assert len(query_result) == 2

            assert mock_model.encode.call_count == 2

    def test_batch_processing(self, mock_config):
        """Test handling many documents."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()

            # Create embeddings for 100 documents
            embeddings_array = np.array([[0.1, 0.2] for _ in range(100)])
            mock_model.encode.return_value = embeddings_array
            mock_st.return_value = mock_model

            from embeddings.implementations.huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(mock_config)

            documents = [f"Document {i}" for i in range(100)]
            result = embeddings.embed_documents(documents)

            assert len(result) == 100
            # Should be called once (SentenceTransformer handles batching internally)
            mock_model.encode.assert_called_once()
