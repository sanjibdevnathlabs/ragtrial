"""
Tests for Anthropic (Voyage AI) embeddings provider.

Unit tests with mocked Voyage API calls.
Following industry best practices - no actual API calls.

Test Coverage:
- Initialization
- embed_documents()
- embed_query()
- get_dimension()
- Input type parameters (document vs query)
- SSL verification configuration
- Error handling
"""

from unittest.mock import MagicMock, patch

import pytest

from config import Config

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_config():
    """Create mock configuration for Anthropic/Voyage (using test.toml)."""
    return Config()


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestAnthropicEmbeddingsInitialization:
    """Test Anthropic embeddings initialization."""

    def test_initialization_success(self, mock_config):
        """Test successful initialization."""
        with patch("voyageai.Client") as mock_voyage_class:
            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            assert embeddings.config is not None
            assert embeddings.model == mock_config.embeddings.anthropic.model
            assert embeddings.dimension == mock_config.embeddings.dimension
            mock_voyage_class.assert_called_once()

    def test_initialization_with_api_key(self, mock_config):
        """Test initialization uses API key from config."""
        with patch("voyageai.Client") as mock_voyage_class:
            from embeddings.implementations.anthropic import AnthropicEmbeddings

            AnthropicEmbeddings(mock_config)

            call_kwargs = mock_voyage_class.call_args[1]
            assert "api_key" in call_kwargs

    def test_initialization_ssl_verification(self, mock_config):
        """Test SSL verification configuration."""
        with patch("voyageai.Client") as mock_voyage_class:
            from embeddings.implementations.anthropic import AnthropicEmbeddings

            AnthropicEmbeddings(mock_config)

            # Verify SSL settings were configured
            mock_voyage_class.assert_called_once()


# ============================================================================
# EMBED DOCUMENTS TESTS
# ============================================================================


class TestEmbedDocuments:
    """Test embed_documents() method."""

    def test_embed_single_document(self, mock_config):
        """Test embedding a single document."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.1, 0.2, 0.3]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            result = embeddings.embed_documents(["Hello world"])

            assert len(result) == 1
            assert result[0] == [0.1, 0.2, 0.3]
            mock_client.embed.assert_called_once()

    def test_embed_multiple_documents(self, mock_config):
        """Test embedding multiple documents."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            result = embeddings.embed_documents(["Text 1", "Text 2"])

            assert len(result) == 2
            assert result[0] == [0.1, 0.2, 0.3]
            assert result[1] == [0.4, 0.5, 0.6]

    def test_embed_documents_uses_document_input_type(self, mock_config):
        """Test documents use input_type='document'."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.1]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)
            embeddings.embed_documents(["Test"])

            call_kwargs = mock_client.embed.call_args[1]
            assert call_kwargs["input_type"] == "document"

    def test_embed_documents_uses_correct_model(self, mock_config):
        """Test correct model is used."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.1]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)
            embeddings.embed_documents(["Test"])

            call_kwargs = mock_client.embed.call_args[1]
            assert call_kwargs["model"] == mock_config.embeddings.anthropic.model

    def test_embed_documents_empty_list(self, mock_config):
        """Test embedding empty list."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = []
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            result = embeddings.embed_documents([])

            assert result == []

    def test_embed_documents_error_handling(self, mock_config):
        """Test error handling in embed_documents."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client
            mock_client.embed.side_effect = Exception("Voyage API Error")

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            with pytest.raises(Exception) as exc_info:
                embeddings.embed_documents(["Test"])

            assert "Voyage API Error" in str(exc_info.value)


# ============================================================================
# EMBED QUERY TESTS
# ============================================================================


class TestEmbedQuery:
    """Test embed_query() method."""

    def test_embed_single_query(self, mock_config):
        """Test embedding a single query."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.7, 0.8, 0.9]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            result = embeddings.embed_query("What is AI?")

            assert result == [0.7, 0.8, 0.9]
            mock_client.embed.assert_called_once()

    def test_embed_query_uses_query_input_type(self, mock_config):
        """Test query uses input_type='query'."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.1]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)
            embeddings.embed_query("Test")

            call_kwargs = mock_client.embed.call_args[1]
            assert call_kwargs["input_type"] == "query"

    def test_embed_query_uses_correct_model(self, mock_config):
        """Test query uses correct model."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.1]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)
            embeddings.embed_query("Query")

            call_kwargs = mock_client.embed.call_args[1]
            assert call_kwargs["model"] == mock_config.embeddings.anthropic.model

    def test_embed_query_error_handling(self, mock_config):
        """Test error handling in embed_query."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client
            mock_client.embed.side_effect = ValueError("Invalid query")

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            with pytest.raises(ValueError):
                embeddings.embed_query("Test")


# ============================================================================
# GET DIMENSION TESTS
# ============================================================================


class TestGetDimension:
    """Test get_dimension() method."""

    def test_get_dimension_returns_config_value(self, mock_config):
        """Test get_dimension returns configured dimension."""
        with patch("voyageai.Client"):
            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            result = embeddings.get_dimension()

            assert result == mock_config.embeddings.dimension
            assert isinstance(result, int)
            assert result > 0

    def test_get_dimension_matches_config(self, mock_config):
        """Test dimension matches configuration."""
        with patch("voyageai.Client"):
            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            assert embeddings.get_dimension() == embeddings.dimension


# ============================================================================
# INPUT TYPE TESTS
# ============================================================================


class TestInputTypeParameter:
    """Test input_type parameter differentiation."""

    def test_different_input_types_for_documents_and_queries(self, mock_config):
        """Test documents and queries use different input_type."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.embeddings = [[0.1]]
            mock_client.embed.return_value = mock_response

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            # Embed documents
            embeddings.embed_documents(["Doc"])
            doc_call_kwargs = mock_client.embed.call_args[1]
            doc_input_type = doc_call_kwargs["input_type"]

            # Embed query
            embeddings.embed_query("Query")
            query_call_kwargs = mock_client.embed.call_args[1]
            query_input_type = query_call_kwargs["input_type"]

            assert doc_input_type != query_input_type
            assert doc_input_type == "document"
            assert query_input_type == "query"


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic usage scenarios with mocks."""

    def test_full_workflow(self, mock_config):
        """Test complete workflow."""
        with patch("voyageai.Client") as mock_voyage_class:
            mock_client = MagicMock()
            mock_voyage_class.return_value = mock_client

            # Mock responses
            doc_response = MagicMock()
            doc_response.embeddings = [[0.1, 0.2], [0.3, 0.4]]

            query_response = MagicMock()
            query_response.embeddings = [[0.5, 0.6]]

            mock_client.embed.side_effect = [doc_response, query_response]

            from embeddings.implementations.anthropic import AnthropicEmbeddings

            embeddings = AnthropicEmbeddings(mock_config)

            # Test documents
            doc_result = embeddings.embed_documents(["Doc 1", "Doc 2"])
            assert len(doc_result) == 2

            # Test query
            query_result = embeddings.embed_query("Query")
            assert len(query_result) == 2  # Query result is a single vector [0.5, 0.6]

            assert mock_client.embed.call_count == 2
