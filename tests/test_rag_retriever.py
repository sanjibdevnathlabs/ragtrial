"""
Tests for DocumentRetriever.

Tests retrieval logic for RAG system.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from app.simple_rag.retriever import DocumentRetriever
from langchain_core.documents import Document
import constants


@pytest.fixture
def mock_config():
    """Mock configuration."""
    config = Mock()
    config.vectorstore.provider = "chroma"
    config.embeddings.provider = "google"
    config.rag.provider = "google"
    config.rag.retrieval_k = 5
    return config


@pytest.fixture
def mock_embeddings():
    """Mock embeddings provider."""
    return Mock()


@pytest.fixture
def mock_vectorstore():
    """Mock vectorstore provider."""
    mock_vs = Mock()
    mock_vs.query.return_value = [
        Document(page_content="Test content 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test content 2", metadata={"source": "test2.txt"}),
    ]
    return mock_vs


class TestDocumentRetrieverInit:
    """Tests for DocumentRetriever initialization."""
    
    def test_init_success(self, mock_config):
        """Test successful initialization."""
        with patch("app.simple_rag.retriever.create_embeddings") as mock_create_emb, \
             patch("app.simple_rag.retriever.create_vectorstore") as mock_create_vs:
            
            mock_create_emb.return_value = Mock()
            mock_create_vs.return_value = Mock()
            
            retriever = DocumentRetriever(mock_config)
            
            assert retriever.config == mock_config
            assert retriever.embeddings is not None
            assert retriever.vectorstore is not None
            
            mock_create_emb.assert_called_once_with(mock_config)
            mock_create_vs.assert_called_once()


class TestDocumentRetrieverRetrieve:
    """Tests for DocumentRetriever.retrieve() method."""
    
    def test_retrieve_success(self, mock_config):
        """Test successful document retrieval."""
        with patch("app.simple_rag.retriever.create_embeddings") as mock_create_emb, \
             patch("app.simple_rag.retriever.create_vectorstore") as mock_create_vs:
            
            mock_create_emb.return_value = Mock()
            mock_vs = Mock()
            # Vectorstore returns dicts, not Document objects
            mock_vs.query.return_value = [
                {"text": "Content 1", "metadata": {"source": "doc1.txt"}},
                {"text": "Content 2", "metadata": {"source": "doc2.txt"}},
            ]
            mock_create_vs.return_value = mock_vs
            
            retriever = DocumentRetriever(mock_config)
            documents = retriever.retrieve("test query")
            
            assert len(documents) == 2
            assert documents[0].page_content == "Content 1"
            assert documents[1].page_content == "Content 2"
            
            mock_vs.query.assert_called_once_with("test query", n_results=constants.DEFAULT_RETRIEVAL_K)
    
    def test_retrieve_empty_query_raises_error(self, mock_config):
        """Test that empty query raises ValueError."""
        with patch("app.simple_rag.retriever.create_embeddings"), \
             patch("app.simple_rag.retriever.create_vectorstore"):
            
            retriever = DocumentRetriever(mock_config)
            
            with pytest.raises(ValueError) as exc_info:
                retriever.retrieve("")
            
            assert constants.ERROR_RAG_INVALID_QUERY in str(exc_info.value)
    
    def test_retrieve_whitespace_query_raises_error(self, mock_config):
        """Test that whitespace-only query raises ValueError."""
        with patch("app.simple_rag.retriever.create_embeddings"), \
             patch("app.simple_rag.retriever.create_vectorstore"):
            
            retriever = DocumentRetriever(mock_config)
            
            with pytest.raises(ValueError):
                retriever.retrieve("   ")
    
    def test_retrieve_invalid_k_too_small(self, mock_config):
        """Test that k < MIN_RETRIEVAL_K raises ValueError."""
        with patch("app.simple_rag.retriever.create_embeddings"), \
             patch("app.simple_rag.retriever.create_vectorstore"):
            
            retriever = DocumentRetriever(mock_config)
            
            with pytest.raises(ValueError) as exc_info:
                retriever.retrieve("test", k=0)
            
            assert "must be between" in str(exc_info.value)
    
    def test_retrieve_invalid_k_too_large(self, mock_config):
        """Test that k > MAX_RETRIEVAL_K raises ValueError."""
        with patch("app.simple_rag.retriever.create_embeddings"), \
             patch("app.simple_rag.retriever.create_vectorstore"):
            
            retriever = DocumentRetriever(mock_config)
            
            with pytest.raises(ValueError) as exc_info:
                retriever.retrieve("test", k=100)
            
            assert "must be between" in str(exc_info.value)
    
    def test_retrieve_custom_k_value(self, mock_config):
        """Test retrieval with custom k value."""
        with patch("app.simple_rag.retriever.create_embeddings"), \
             patch("app.simple_rag.retriever.create_vectorstore") as mock_create_vs:
            
            mock_vs = Mock()
            # Vectorstore returns dicts, not Document objects
            mock_vs.query.return_value = [{"text": "test", "metadata": {}}]
            mock_create_vs.return_value = mock_vs
            
            retriever = DocumentRetriever(mock_config)
            retriever.retrieve("test query", k=3)
            
            mock_vs.query.assert_called_once_with("test query", n_results=3)
    
    def test_retrieve_vectorstore_error_raises_runtime_error(self, mock_config):
        """Test that vectorstore error raises RuntimeError."""
        with patch("app.simple_rag.retriever.create_embeddings"), \
             patch("app.simple_rag.retriever.create_vectorstore") as mock_create_vs:
            
            mock_vs = Mock()
            mock_vs.query.side_effect = Exception("Vectorstore error")
            mock_create_vs.return_value = mock_vs
            
            retriever = DocumentRetriever(mock_config)
            
            with pytest.raises(RuntimeError) as exc_info:
                retriever.retrieve("test query")
            
            assert constants.ERROR_RAG_RETRIEVAL_FAILED in str(exc_info.value)
    
    def test_retrieve_no_documents_found(self, mock_config):
        """Test retrieval when no documents found."""
        with patch("app.simple_rag.retriever.create_embeddings"), \
             patch("app.simple_rag.retriever.create_vectorstore") as mock_create_vs:
            
            mock_vs = Mock()
            mock_vs.query.return_value = []
            mock_create_vs.return_value = mock_vs
            
            retriever = DocumentRetriever(mock_config)
            documents = retriever.retrieve("test query")
            
            assert len(documents) == 0

