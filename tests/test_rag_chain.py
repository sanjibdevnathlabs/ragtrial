"""
Tests for RAG Chain.

Tests main RAG chain orchestration.
"""

from unittest.mock import Mock, patch

import pytest
from langchain_core.documents import Document

import constants
from app.chain_rag.chain import RAGChain


@pytest.fixture
def mock_config():
    """Mock configuration."""
    config = Mock()
    config.vectorstore.provider = "chroma"
    config.embeddings.provider = "google"
    config.rag.provider = "google"
    config.rag.google.model = "gemini-1.5-flash"
    config.rag.google.temperature = 0.1
    config.rag.google.max_tokens = 1000
    config.rag.google.api_key = "test-api-key"
    return config


@pytest.fixture
def mock_retriever():
    """Mock document retriever."""
    retriever = Mock()
    retriever.retrieve.return_value = [
        Document(page_content="Content 1", metadata={"source": "doc1.txt"}),
        Document(page_content="Content 2", metadata={"source": "doc2.txt"}),
    ]
    return retriever


@pytest.fixture
def mock_llm():
    """Mock LLM."""
    llm = Mock()
    response = Mock()
    response.content = "This is the generated answer."
    llm.invoke.return_value = response
    return llm


class TestRAGChainInit:
    """Tests for RAGChain initialization."""

    def test_init_success(self, mock_config):
        """Test successful initialization."""
        with patch(
            "app.chain_rag.chain.DocumentRetriever"
        ) as mock_retriever_class, patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch(
            "llm.factory.create_llm"
        ) as mock_create_llm:

            mock_retriever_class.return_value = Mock()
            mock_create_prompt.return_value = Mock()
            mock_create_llm.return_value = Mock()

            chain = RAGChain(mock_config)

            assert chain.config == mock_config
            assert chain.retriever is not None
            assert chain.prompt is not None
            assert chain.llm is not None

    def test_init_calls_document_retriever(self, mock_config):
        """Test that initialization creates DocumentRetriever."""
        with patch(
            "app.chain_rag.chain.DocumentRetriever"
        ) as mock_retriever_class, patch(
            "app.chain_rag.chain.create_rag_prompt"
        ), patch(
            "llm.factory.create_llm"
        ):

            RAGChain(mock_config)

            mock_retriever_class.assert_called_once_with(mock_config)

    def test_init_creates_prompt(self, mock_config):
        """Test that initialization creates RAG prompt."""
        with patch("app.chain_rag.chain.DocumentRetriever"), patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch("llm.factory.create_llm"):

            RAGChain(mock_config)

            mock_create_prompt.assert_called_once()

    def test_init_creates_llm_via_factory(self, mock_config):
        """Test that LLM is created via factory."""
        with patch("app.chain_rag.chain.DocumentRetriever"), patch(
            "app.chain_rag.chain.create_rag_prompt"
        ), patch("llm.factory.create_llm") as mock_create_llm:

            RAGChain(mock_config)

            mock_create_llm.assert_called_once_with(mock_config)

    def test_init_failure_raises_runtime_error(self, mock_config):
        """Test that initialization failure raises RuntimeError."""
        with patch("app.chain_rag.chain.DocumentRetriever") as mock_retriever_class:

            mock_retriever_class.side_effect = Exception("Init error")

            with pytest.raises(RuntimeError) as exc_info:
                RAGChain(mock_config)

            assert constants.ERROR_RAG_CHAIN_INIT_FAILED in str(exc_info.value)


class TestRAGChainQuery:
    """Tests for RAGChain.query() method."""

    def test_query_success(self, mock_config):
        """Test successful query processing."""
        with patch(
            "app.chain_rag.chain.DocumentRetriever"
        ) as mock_retriever_class, patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch(
            "llm.factory.create_llm"
        ) as mock_llm_class:

            mock_retriever = Mock()
            mock_retriever.retrieve.return_value = [
                Document(page_content="Content", metadata={"source": "test.txt"})
            ]
            mock_retriever_class.return_value = mock_retriever

            mock_prompt = Mock()
            mock_prompt.format_messages.return_value = []
            mock_create_prompt.return_value = mock_prompt

            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Answer text"
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm

            chain = RAGChain(mock_config)
            response = chain.query("What is the answer?")

            assert response[constants.RESPONSE_KEY_ANSWER] == "Answer text"
            assert response[constants.RESPONSE_KEY_QUERY] == "What is the answer?"
            assert constants.RESPONSE_KEY_SOURCES in response
            assert constants.RESPONSE_KEY_HAS_ANSWER in response

    def test_query_empty_question_raises_error(self, mock_config):
        """Test that empty question raises ValueError."""
        with patch("app.chain_rag.chain.DocumentRetriever"), patch(
            "app.chain_rag.chain.create_rag_prompt"
        ), patch("llm.factory.create_llm"):

            chain = RAGChain(mock_config)

            with pytest.raises(ValueError) as exc_info:
                chain.query("")

            assert constants.ERROR_RAG_INVALID_QUERY in str(exc_info.value)

    def test_query_whitespace_question_raises_error(self, mock_config):
        """Test that whitespace question raises ValueError."""
        with patch("app.chain_rag.chain.DocumentRetriever"), patch(
            "app.chain_rag.chain.create_rag_prompt"
        ), patch("llm.factory.create_llm"):

            chain = RAGChain(mock_config)

            with pytest.raises(ValueError):
                chain.query("   ")

    def test_query_no_documents_found(self, mock_config):
        """Test query when no documents are found."""
        with patch(
            "app.chain_rag.chain.DocumentRetriever"
        ) as mock_retriever_class, patch(
            "app.chain_rag.chain.create_rag_prompt"
        ), patch(
            "llm.factory.create_llm"
        ):

            mock_retriever = Mock()
            mock_retriever.retrieve.return_value = []
            mock_retriever_class.return_value = mock_retriever

            chain = RAGChain(mock_config)
            response = chain.query("test question")

            assert (
                response[constants.RESPONSE_KEY_ANSWER]
                == constants.MSG_RAG_NO_RELEVANT_DOCS
            )
            assert response[constants.RESPONSE_KEY_RETRIEVAL_COUNT] == 0
            assert response[constants.RESPONSE_KEY_HAS_ANSWER] is False

    def test_query_calls_retriever(self, mock_config):
        """Test that query calls retriever."""
        with patch(
            "app.chain_rag.chain.DocumentRetriever"
        ) as mock_retriever_class, patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch(
            "llm.factory.create_llm"
        ) as mock_llm_class:

            mock_retriever = Mock()
            mock_retriever.retrieve.return_value = [
                Document(page_content="Content", metadata={"source": "test.txt"})
            ]
            mock_retriever_class.return_value = mock_retriever

            mock_prompt = Mock()
            mock_prompt.format_messages.return_value = []
            mock_create_prompt.return_value = mock_prompt

            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Answer"
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm

            chain = RAGChain(mock_config)
            chain.query("test question")

            mock_retriever.retrieve.assert_called_once_with("test question")

    def test_query_calls_llm(self, mock_config):
        """Test that query calls LLM."""
        with patch(
            "app.chain_rag.chain.DocumentRetriever"
        ) as mock_retriever_class, patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch(
            "llm.factory.create_llm"
        ) as mock_llm_class:

            mock_retriever = Mock()
            mock_retriever.retrieve.return_value = [
                Document(page_content="Content", metadata={"source": "test.txt"})
            ]
            mock_retriever_class.return_value = mock_retriever

            mock_prompt = Mock()
            mock_prompt.format_messages.return_value = ["formatted_messages"]
            mock_create_prompt.return_value = mock_prompt

            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Answer"
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm

            chain = RAGChain(mock_config)
            chain.query("test question")

            mock_llm.invoke.assert_called_once_with(["formatted_messages"])

    def test_query_llm_failure_raises_runtime_error(self, mock_config):
        """Test that LLM failure raises RuntimeError."""
        with patch(
            "app.chain_rag.chain.DocumentRetriever"
        ) as mock_retriever_class, patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch(
            "llm.factory.create_llm"
        ) as mock_llm_class:

            mock_retriever = Mock()
            mock_retriever.retrieve.return_value = [
                Document(page_content="Content", metadata={"source": "test.txt"})
            ]
            mock_retriever_class.return_value = mock_retriever

            mock_prompt = Mock()
            mock_prompt.format_messages.return_value = []
            mock_create_prompt.return_value = mock_prompt

            mock_llm = Mock()
            mock_llm.invoke.side_effect = Exception("LLM error")
            mock_llm_class.return_value = mock_llm

            chain = RAGChain(mock_config)

            with pytest.raises(RuntimeError) as exc_info:
                chain.query("test question")

            assert constants.ERROR_RAG_QUERY_FAILED in str(exc_info.value)


class TestRAGChainGenerateAnswer:
    """Tests for RAGChain._generate_answer() method."""

    def test_generate_answer_formats_prompt(self, mock_config):
        """Test that answer generation formats prompt."""
        with patch("app.chain_rag.chain.DocumentRetriever"), patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch(
            "llm.factory.create_llm"
        ) as mock_llm_class, patch(
            "app.chain_rag.chain.format_context"
        ) as mock_format_context:

            mock_format_context.return_value = "Formatted context"

            mock_prompt = Mock()
            mock_prompt.format_messages.return_value = []
            mock_create_prompt.return_value = mock_prompt

            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Answer"
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm

            chain = RAGChain(mock_config)
            documents = [Document(page_content="Test", metadata={})]
            chain._generate_answer("test question", documents)

            mock_format_context.assert_called_once_with(documents)
            mock_prompt.format_messages.assert_called_once_with(
                context="Formatted context", question="test question"
            )

    def test_generate_answer_llm_error_raises_runtime_error(self, mock_config):
        """Test that LLM error raises RuntimeError."""
        with patch("app.chain_rag.chain.DocumentRetriever"), patch(
            "app.chain_rag.chain.create_rag_prompt"
        ) as mock_create_prompt, patch("llm.factory.create_llm") as mock_llm_class:

            mock_prompt = Mock()
            mock_prompt.format_messages.return_value = []
            mock_create_prompt.return_value = mock_prompt

            mock_llm = Mock()
            mock_llm.invoke.side_effect = Exception("LLM failed")
            mock_llm_class.return_value = mock_llm

            chain = RAGChain(mock_config)
            documents = [Document(page_content="Test", metadata={})]

            with pytest.raises(RuntimeError) as exc_info:
                chain._generate_answer("test", documents)

            assert constants.ERROR_RAG_LLM_FAILED in str(exc_info.value)
