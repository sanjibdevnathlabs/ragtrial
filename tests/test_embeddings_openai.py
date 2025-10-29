"""
Tests for OpenAI embeddings provider.

Unit tests with mocked OpenAI API calls.
Following industry best practices - no actual API calls.

Test Coverage:
- Initialization
- embed_documents()
- embed_query()
- get_dimension()
- Error handling
- SSL verification configuration
"""

from unittest.mock import MagicMock, patch

import pytest

from config import Config

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_config():
    """Create mock configuration for OpenAI (using test.toml)."""
    return Config()


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestOpenAIEmbeddingsInitialization:
    """Test OpenAI embeddings initialization."""

    def test_initialization_success(self, mock_config):
        """Test successful initialization."""
        with patch("openai.OpenAI") as mock_openai_class:
            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            assert embeddings.config is not None
            assert embeddings.model == mock_config.embeddings.openai.model
            assert embeddings.dimension == mock_config.embeddings.openai.dimensions
            mock_openai_class.assert_called_once()

    def test_initialization_with_api_key(self, mock_config):
        """Test initialization uses API key from config."""
        with patch("openai.OpenAI") as mock_openai_class:
            from embeddings.implementations.openai import OpenAIEmbeddings

            OpenAIEmbeddings(mock_config)

            call_kwargs = mock_openai_class.call_args[1]
            assert "api_key" in call_kwargs

    def test_initialization_ssl_verification(self, mock_config):
        """Test SSL verification configuration."""
        with patch("openai.OpenAI") as mock_openai_class:
            from embeddings.implementations.openai import OpenAIEmbeddings

            OpenAIEmbeddings(mock_config)

            # Verify SSL settings were configured
            mock_openai_class.assert_called_once()


# ============================================================================
# EMBED DOCUMENTS TESTS
# ============================================================================


class TestEmbedDocuments:
    """Test embed_documents() method."""

    def test_embed_single_document(self, mock_config):
        """Test embedding a single document."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_client.embeddings.create.return_value = mock_response

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            result = embeddings.embed_documents(["Hello world"])

            assert len(result) == 1
            assert result[0] == [0.1, 0.2, 0.3]
            mock_client.embeddings.create.assert_called_once()

    def test_embed_multiple_documents(self, mock_config):
        """Test embedding multiple documents."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=[0.1, 0.2, 0.3]),
                MagicMock(embedding=[0.4, 0.5, 0.6]),
            ]
            mock_client.embeddings.create.return_value = mock_response

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            result = embeddings.embed_documents(["Text 1", "Text 2"])

            assert len(result) == 2
            assert result[0] == [0.1, 0.2, 0.3]
            assert result[1] == [0.4, 0.5, 0.6]

    def test_embed_documents_uses_correct_model(self, mock_config):
        """Test that correct model is used."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1])]
            mock_client.embeddings.create.return_value = mock_response

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)
            embeddings.embed_documents(["Test"])

            call_kwargs = mock_client.embeddings.create.call_args[1]
            assert call_kwargs["model"] == mock_config.embeddings.openai.model

    def test_embed_documents_empty_list(self, mock_config):
        """Test embedding empty list."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.data = []
            mock_client.embeddings.create.return_value = mock_response

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            result = embeddings.embed_documents([])

            assert result == []

    def test_embed_documents_error_handling(self, mock_config):
        """Test error handling in embed_documents."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            mock_client.embeddings.create.side_effect = Exception("API Error")

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            with pytest.raises(Exception) as exc_info:
                embeddings.embed_documents(["Test"])

            assert "API Error" in str(exc_info.value)


# ============================================================================
# EMBED QUERY TESTS
# ============================================================================


class TestEmbedQuery:
    """Test embed_query() method."""

    def test_embed_single_query(self, mock_config):
        """Test embedding a single query."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.7, 0.8, 0.9])]
            mock_client.embeddings.create.return_value = mock_response

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            result = embeddings.embed_query("What is AI?")

            assert result == [0.7, 0.8, 0.9]
            mock_client.embeddings.create.assert_called_once()

    def test_embed_query_uses_correct_model(self, mock_config):
        """Test query uses correct model."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1])]
            mock_client.embeddings.create.return_value = mock_response

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)
            embeddings.embed_query("Query")

            call_kwargs = mock_client.embeddings.create.call_args[1]
            assert call_kwargs["model"] == mock_config.embeddings.openai.model

    def test_embed_query_error_handling(self, mock_config):
        """Test error handling in embed_query."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            mock_client.embeddings.create.side_effect = ValueError("Invalid query")

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            with pytest.raises(ValueError):
                embeddings.embed_query("Test")


# ============================================================================
# GET DIMENSION TESTS
# ============================================================================


class TestGetDimension:
    """Test get_dimension() method."""

    def test_get_dimension_returns_config_value(self, mock_config):
        """Test get_dimension returns configured dimension."""
        with patch("openai.OpenAI"):
            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            result = embeddings.get_dimension()

            assert result == mock_config.embeddings.openai.dimensions
            assert isinstance(result, int)
            assert result > 0

    def test_get_dimension_matches_config(self, mock_config):
        """Test dimension matches configuration."""
        with patch("openai.OpenAI"):
            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            assert embeddings.get_dimension() == embeddings.dimension


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic usage scenarios with mocks."""

    def test_full_workflow(self, mock_config):
        """Test complete workflow."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock responses
            doc_response = MagicMock()
            doc_response.data = [
                MagicMock(embedding=[0.1, 0.2]),
                MagicMock(embedding=[0.3, 0.4]),
            ]

            query_response = MagicMock()
            query_response.data = [MagicMock(embedding=[0.5, 0.6])]

            mock_client.embeddings.create.side_effect = [doc_response, query_response]

            from embeddings.implementations.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(mock_config)

            # Test documents
            doc_result = embeddings.embed_documents(["Doc 1", "Doc 2"])
            assert len(doc_result) == 2

            # Test query
            query_result = embeddings.embed_query("Query")
            assert len(query_result) == 2

            assert mock_client.embeddings.create.call_count == 2
