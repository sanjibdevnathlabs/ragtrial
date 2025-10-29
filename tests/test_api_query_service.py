"""
Unit tests for QueryService.

Tests the query service with mocked RAG chain.
"""

from unittest.mock import Mock, patch

import pytest

import constants
from app.modules.query.service import QueryService


@pytest.fixture
def mock_rag_chain():
    """Create a mock RAG chain."""
    mock = Mock()
    mock.query.return_value = {
        constants.RESPONSE_KEY_ANSWER: "Test answer",
        constants.RESPONSE_KEY_SOURCES: [],
        constants.RESPONSE_KEY_HAS_ANSWER: True,
        constants.RESPONSE_KEY_QUERY: "test question",
    }
    return mock


class TestQueryServiceInitialization:
    """Test query service initialization and singleton pattern."""

    def test_service_is_singleton(self):
        """Test that QueryService follows singleton pattern."""
        service1 = QueryService()
        service2 = QueryService()

        assert service1 is service2

    def test_service_initializes_without_rag_chain(self):
        """Test that service initializes without creating RAG chain."""
        service = QueryService()

        assert service._rag_chain is None
        assert service._config is None  # Config is lazy-loaded


class TestQueryProcessing:
    """Test query processing functionality."""

    @patch("app.modules.query.service.RAGChain")
    def test_query_success(self, mock_rag_class, mock_rag_chain):
        """Test successful query processing."""
        mock_rag_class.return_value = mock_rag_chain

        service = QueryService()
        result = service.query("What is RAG?")

        assert result is not None
        assert constants.RESPONSE_KEY_ANSWER in result
        assert constants.RESPONSE_KEY_SOURCES in result
        assert constants.RESPONSE_KEY_HAS_ANSWER in result

        mock_rag_chain.query.assert_called_once_with("What is RAG?")

    @patch("app.modules.query.service.RAGChain")
    def test_query_initializes_rag_chain_lazily(self, mock_rag_class, mock_rag_chain):
        """Test that RAG chain is initialized on first query."""
        mock_rag_class.return_value = mock_rag_chain

        service = QueryService()
        assert service._rag_chain is None

        service.query("test question")

        assert service._rag_chain is not None
        mock_rag_class.assert_called_once()

    @patch("app.modules.query.service.RAGChain")
    def test_query_reuses_rag_chain(self, mock_rag_class, mock_rag_chain):
        """Test that RAG chain is reused across queries."""
        mock_rag_class.return_value = mock_rag_chain

        service = QueryService()
        service.query("question 1")
        service.query("question 2")

        mock_rag_class.assert_called_once()
        assert mock_rag_chain.query.call_count == 2

    @patch("app.modules.query.service.RAGChain")
    def test_query_with_chain_initialization_failure(self, mock_rag_class):
        """Test query when RAG chain initialization fails."""
        mock_rag_class.side_effect = Exception("Init failed")

        service = QueryService()

        with pytest.raises(RuntimeError) as exc_info:
            service.query("test question")

        assert constants.ERROR_RAG_CHAIN_INITIALIZATION_FAILED in str(exc_info.value)

    @patch("app.modules.query.service.RAGChain")
    def test_query_with_processing_failure(self, mock_rag_class, mock_rag_chain):
        """Test query when processing fails."""
        mock_rag_chain.query.side_effect = Exception("Query failed")
        mock_rag_class.return_value = mock_rag_chain

        service = QueryService()

        with pytest.raises(ValueError) as exc_info:
            service.query("test question")

        assert constants.ERROR_QUERY_PROCESSING_FAILED in str(exc_info.value)


class TestHealthCheck:
    """Test health check functionality."""

    def test_health_check_before_initialization(self):
        """Test health check when RAG chain not initialized."""
        service = QueryService()

        health = service.health_check()

        assert "rag_initialized" in health
        assert health["rag_initialized"] is False
        assert "provider" in health
        assert "model" in health

    @patch("app.modules.query.service.RAGChain")
    def test_health_check_after_initialization(self, mock_rag_class, mock_rag_chain):
        """Test health check when RAG chain is initialized."""
        mock_rag_class.return_value = mock_rag_chain

        service = QueryService()
        service.query("test")

        health = service.health_check()

        assert health["rag_initialized"] is True

    def test_get_model_name_google(self):
        """Test getting model name for Google provider."""
        service = QueryService()
        service._ensure_config_initialized()
        service._config.rag.provider = constants.LLM_PROVIDER_GOOGLE

        model_name = service._get_model_name()

        assert model_name == service._config.rag.google.model

    def test_get_model_name_openai(self):
        """Test getting model name for OpenAI provider."""
        service = QueryService()
        service._ensure_config_initialized()
        service._config.rag.provider = constants.LLM_PROVIDER_OPENAI

        model_name = service._get_model_name()

        assert model_name == service._config.rag.openai.model

    def test_get_model_name_anthropic(self):
        """Test getting model name for Anthropic provider."""
        service = QueryService()
        service._ensure_config_initialized()
        service._config.rag.provider = constants.LLM_PROVIDER_ANTHROPIC

        model_name = service._get_model_name()

        assert model_name == service._config.rag.anthropic.model

    def test_get_model_name_unknown_provider(self):
        """Test getting model name for unknown provider."""
        service = QueryService()
        service._ensure_config_initialized()
        service._config.rag.provider = "unknown_provider"

        model_name = service._get_model_name()

        assert model_name == "unknown"


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("app.modules.query.service.RAGChain")
    def test_query_with_empty_sources(self, mock_rag_class, mock_rag_chain):
        """Test query when no sources are found."""
        mock_rag_chain.query.return_value = {
            constants.RESPONSE_KEY_ANSWER: "No answer found",
            constants.RESPONSE_KEY_SOURCES: [],
            constants.RESPONSE_KEY_HAS_ANSWER: False,
            constants.RESPONSE_KEY_QUERY: "obscure question",
        }
        mock_rag_class.return_value = mock_rag_chain

        service = QueryService()
        result = service.query("obscure question")

        assert result[constants.RESPONSE_KEY_HAS_ANSWER] is False
        assert len(result[constants.RESPONSE_KEY_SOURCES]) == 0

    @patch("app.modules.query.service.RAGChain")
    def test_query_with_multiple_sources(self, mock_rag_class, mock_rag_chain):
        """Test query with multiple source documents."""
        mock_rag_chain.query.return_value = {
            constants.RESPONSE_KEY_ANSWER: "Answer with sources",
            constants.RESPONSE_KEY_SOURCES: [
                {
                    "metadata": {constants.META_SOURCE: "doc1.txt"},
                    "content": "content1",
                },
                {
                    "metadata": {constants.META_SOURCE: "doc2.pdf"},
                    "content": "content2",
                },
                {"metadata": {constants.META_SOURCE: "doc3.md"}, "content": "content3"},
            ],
            constants.RESPONSE_KEY_HAS_ANSWER: True,
            constants.RESPONSE_KEY_QUERY: "test question",
        }
        mock_rag_class.return_value = mock_rag_chain

        service = QueryService()
        result = service.query("test question")

        assert len(result[constants.RESPONSE_KEY_SOURCES]) == 3
