"""
Tests for ChromaDB vectorstore implementation.

Unit tests with FULL MOCKING - no actual database operations.
Following industry best practices:
- No database connections
- No file system writes
- Fast, isolated tests suitable for CI/CD

Test Coverage:
- Initialization with config and embeddings
- Collection creation and retrieval
- Document addition (single and batch)
- Query operations
- Delete operations
- Statistics retrieval
- Collection clearing
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from config import Config
from vectorstore.implementations.chroma import ChromaVectorStore
from embeddings.base import EmbeddingsProtocol


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_embeddings():
    """Create mock embeddings provider."""
    embeddings = Mock(spec=EmbeddingsProtocol)
    embeddings.embed_documents.return_value = [
        [0.1, 0.2, 0.3],  # Vector for doc 1
        [0.4, 0.5, 0.6],  # Vector for doc 2
    ]
    embeddings.embed_query.return_value = [0.7, 0.8, 0.9]
    embeddings.get_dimension.return_value = 768
    return embeddings


@pytest.fixture
def mock_config():
    """Create config with Chroma settings (uses test.toml)."""
    return Config()


@pytest.fixture
def mock_chroma_client():
    """Create mock ChromaDB client."""
    client = MagicMock()
    collection = MagicMock()
    collection.count.return_value = 5
    collection.add.return_value = None
    collection.query.return_value = {
        "ids": [["doc_1", "doc_2"]],
        "documents": [["Document 1 text", "Document 2 text"]],
        "metadatas": [[{"source": "a.pdf"}, {"source": "b.pdf"}]],
        "distances": [[0.1, 0.2]]
    }
    collection.delete.return_value = None
    client.get_collection.return_value = collection
    client.create_collection.return_value = collection
    return client


@pytest.fixture
def chroma_vectorstore(mock_config, mock_embeddings, mock_chroma_client):
    """Create ChromaVectorStore with mocked dependencies."""
    with patch("chromadb.Client", return_value=mock_chroma_client):
        with patch("pathlib.Path.mkdir"):
            vectorstore = ChromaVectorStore(mock_config, mock_embeddings)
            return vectorstore


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestInitialization:
    """Test ChromaVectorStore initialization."""

    def test_initialization_success(self, mock_config, mock_embeddings, mock_chroma_client):
        """Test successful initialization."""
        with patch("chromadb.Client", return_value=mock_chroma_client):
            with patch("pathlib.Path.mkdir"):
                vectorstore = ChromaVectorStore(mock_config, mock_embeddings)
                
                assert vectorstore is not None
                assert vectorstore.embeddings == mock_embeddings
                assert vectorstore.config == mock_config
                assert vectorstore.collection_name == "test_collection"

    def test_creates_persist_directory(self, mock_config, mock_embeddings, mock_chroma_client):
        """Test that persist directory is created."""
        with patch("chromadb.Client", return_value=mock_chroma_client):
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                vectorstore = ChromaVectorStore(mock_config, mock_embeddings)
                
                assert vectorstore is not None
                mock_mkdir.assert_called_once()

    def test_stores_configuration(self, mock_config, mock_embeddings, mock_chroma_client):
        """Test configuration is stored correctly."""
        with patch("chromadb.Client", return_value=mock_chroma_client):
            with patch("pathlib.Path.mkdir"):
                vectorstore = ChromaVectorStore(mock_config, mock_embeddings)
                
                assert vectorstore.collection_name == "test_collection"
                assert "test" in vectorstore.persist_directory.lower()


# ============================================================================
# COLLECTION INITIALIZATION TESTS
# ============================================================================


class TestCollectionInitialization:
    """Test collection initialization (create/get)."""

    def test_initialize_gets_existing_collection(
        self, chroma_vectorstore, mock_chroma_client
    ):
        """Test initialize retrieves existing collection."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_chroma_client.get_collection.return_value = mock_collection
        
        chroma_vectorstore.initialize()
        
        assert chroma_vectorstore.collection is not None
        mock_chroma_client.get_collection.assert_called_once_with(
            name="test_collection"
        )

    def test_initialize_creates_new_collection_if_not_exists(
        self, chroma_vectorstore, mock_chroma_client
    ):
        """Test initialize creates collection if it doesn't exist."""
        # Simulate collection not found
        mock_chroma_client.get_collection.side_effect = Exception("Not found")
        mock_collection = MagicMock()
        mock_chroma_client.create_collection.return_value = mock_collection
        
        chroma_vectorstore.initialize()
        
        assert chroma_vectorstore.collection is not None
        mock_chroma_client.create_collection.assert_called_once()


# ============================================================================
# ADD DOCUMENTS TESTS
# ============================================================================


class TestAddDocuments:
    """Test adding documents to vectorstore."""

    def test_add_documents_success(self, chroma_vectorstore, mock_embeddings):
        """Test successful document addition."""
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        texts = ["Document 1", "Document 2"]
        metadatas = [{"source": "a.pdf"}, {"source": "b.pdf"}]
        
        chroma_vectorstore.add_documents(texts, metadatas)
        
        # Verify embeddings were generated
        mock_embeddings.embed_documents.assert_called_once_with(texts)
        
        # Verify collection.add was called
        mock_collection.add.assert_called_once()

    def test_add_documents_generates_ids_if_not_provided(
        self, chroma_vectorstore, mock_embeddings
    ):
        """Test IDs are auto-generated if not provided."""
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        texts = ["Document 1", "Document 2"]
        
        chroma_vectorstore.add_documents(texts)
        
        # Check that IDs were generated (UUID format)
        call_args = mock_collection.add.call_args
        ids = call_args.kwargs.get("ids")
        assert ids is not None
        assert len(ids) == 2

    def test_add_documents_uses_provided_ids(
        self, chroma_vectorstore, mock_embeddings
    ):
        """Test provided IDs are used."""
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        texts = ["Document 1"]
        ids = ["custom_id_1"]
        
        chroma_vectorstore.add_documents(texts, ids=ids)
        
        call_args = mock_collection.add.call_args
        used_ids = call_args.kwargs.get("ids")
        assert used_ids == ids

    def test_add_documents_handles_empty_metadatas(
        self, chroma_vectorstore, mock_embeddings
    ):
        """Test adding documents without metadata."""
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        texts = ["Document 1"]
        
        chroma_vectorstore.add_documents(texts)
        
        mock_collection.add.assert_called_once()


# ============================================================================
# QUERY TESTS
# ============================================================================


class TestQuery:
    """Test querying the vectorstore."""

    def test_query_success(self, chroma_vectorstore, mock_embeddings):
        """Test successful query."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc_1", "doc_2"]],
            "documents": [["Text 1", "Text 2"]],
            "metadatas": [[{"source": "a.pdf"}, {"source": "b.pdf"}]],
            "distances": [[0.1, 0.2]]
        }
        chroma_vectorstore.collection = mock_collection
        
        results = chroma_vectorstore.query("test query", n_results=2)
        
        # Verify query embedding was generated
        mock_embeddings.embed_query.assert_called_once_with("test query")
        
        # Verify collection was queried
        mock_collection.query.assert_called_once()
        
        # Verify results format
        assert len(results) == 2
        assert results[0]["id"] == "doc_1"
        assert results[0]["text"] == "Text 1"
        assert results[0]["metadata"] == {"source": "a.pdf"}
        assert results[0]["distance"] == 0.1

    def test_query_with_metadata_filter(self, chroma_vectorstore, mock_embeddings):
        """Test query with metadata filter."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc_1"]],
            "documents": [["Text 1"]],
            "metadatas": [[{"source": "a.pdf"}]],
            "distances": [[0.1]]
        }
        chroma_vectorstore.collection = mock_collection
        
        where_filter = {"source": "a.pdf"}
        results = chroma_vectorstore.query("test query", where=where_filter)
        
        # Verify where filter was passed
        call_args = mock_collection.query.call_args
        assert call_args.kwargs.get("where") == where_filter

    def test_query_respects_n_results(self, chroma_vectorstore, mock_embeddings):
        """Test query respects n_results parameter."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc_1", "doc_2", "doc_3"]],
            "documents": [["Text 1", "Text 2", "Text 3"]],
            "metadatas": [[{}, {}, {}]],
            "distances": [[0.1, 0.2, 0.3]]
        }
        chroma_vectorstore.collection = mock_collection
        
        results = chroma_vectorstore.query("test query", n_results=10)
        
        call_args = mock_collection.query.call_args
        assert call_args.kwargs.get("n_results") == 10


# ============================================================================
# DELETE TESTS
# ============================================================================


class TestDelete:
    """Test deleting documents from vectorstore."""

    def test_delete_documents_by_ids(self, chroma_vectorstore):
        """Test deleting documents by IDs."""
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        ids_to_delete = ["doc_1", "doc_2", "doc_3"]
        chroma_vectorstore.delete(ids_to_delete)
        
        mock_collection.delete.assert_called_once_with(ids=ids_to_delete)

    def test_delete_single_document(self, chroma_vectorstore):
        """Test deleting a single document."""
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        chroma_vectorstore.delete(["doc_1"])
        
        mock_collection.delete.assert_called_once_with(ids=["doc_1"])


# ============================================================================
# STATISTICS TESTS
# ============================================================================


class TestStatistics:
    """Test retrieving vectorstore statistics."""

    def test_get_stats_returns_count(self, chroma_vectorstore):
        """Test get_stats returns document count."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 42
        chroma_vectorstore.collection = mock_collection
        
        stats = chroma_vectorstore.get_stats()
        
        assert stats["count"] == 42
        assert stats["collection_name"] == "test_collection"

    def test_get_stats_returns_collection_info(self, chroma_vectorstore):
        """Test get_stats returns collection information."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        chroma_vectorstore.collection = mock_collection
        
        stats = chroma_vectorstore.get_stats()
        
        assert "count" in stats
        assert "collection_name" in stats
        assert "persist_directory" in stats
        assert "distance_function" in stats
        assert "initialized" in stats
        assert stats["initialized"] is True


# ============================================================================
# CLEAR TESTS
# ============================================================================


class TestClear:
    """Test clearing all documents from collection."""

    def test_clear_deletes_all_documents(self, chroma_vectorstore, mock_chroma_client):
        """Test clear removes all documents."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.get.return_value = {"ids": ["doc_1", "doc_2", "doc_3"]}
        chroma_vectorstore.collection = mock_collection
        
        chroma_vectorstore.clear()
        
        # Verify get was called to retrieve all IDs
        mock_collection.get.assert_called_once()
        
        # Verify delete was called with all IDs
        mock_collection.delete.assert_called_once()

    def test_clear_handles_empty_collection(self, chroma_vectorstore):
        """Test clear handles empty collection gracefully."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.get.return_value = {"ids": []}
        chroma_vectorstore.collection = mock_collection
        
        chroma_vectorstore.clear()
        
        # Should still call get, but might not call delete
        mock_collection.get.assert_called_once()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_add_documents_handles_embedding_error(
        self, chroma_vectorstore, mock_embeddings
    ):
        """Test error handling when embeddings fail."""
        # Initialize collection first
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        # Make embeddings fail
        mock_embeddings.embed_documents.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            chroma_vectorstore.add_documents(["Document 1"])
        
        assert "API Error" in str(exc_info.value)

    def test_query_handles_embedding_error(
        self, chroma_vectorstore, mock_embeddings
    ):
        """Test error handling when query embedding fails."""
        # Initialize collection first
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        # Make embeddings fail
        mock_embeddings.embed_query.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            chroma_vectorstore.query("test query")
        
        assert "API Error" in str(exc_info.value)


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic workflows (still fully mocked)."""

    def test_full_workflow_add_query_delete(
        self, chroma_vectorstore, mock_embeddings
    ):
        """Test complete workflow: initialize, add, query, delete."""
        # Setup mock collection
        mock_collection = MagicMock()
        mock_collection.count.return_value = 2
        mock_collection.query.return_value = {
            "ids": [["doc_1"]],
            "documents": [["Document 1 text"]],
            "metadatas": [[{"source": "a.pdf"}]],
            "distances": [[0.1]]
        }
        chroma_vectorstore.collection = mock_collection
        
        # 1. Add documents
        texts = ["Document 1", "Document 2"]
        chroma_vectorstore.add_documents(texts)
        assert mock_collection.add.called
        
        # 2. Query
        results = chroma_vectorstore.query("test query", n_results=5)
        assert len(results) == 1
        assert results[0]["id"] == "doc_1"
        
        # 3. Get stats
        stats = chroma_vectorstore.get_stats()
        assert stats["count"] == 2
        
        # 4. Delete
        chroma_vectorstore.delete(["doc_1"])
        mock_collection.delete.assert_called_with(ids=["doc_1"])

    def test_batch_operations(self, chroma_vectorstore, mock_embeddings):
        """Test batch document operations."""
        mock_collection = MagicMock()
        chroma_vectorstore.collection = mock_collection
        
        # Add batch of documents
        texts = [f"Document {i}" for i in range(100)]
        metadatas = [{"source": f"file_{i}.pdf"} for i in range(100)]
        
        chroma_vectorstore.add_documents(texts, metadatas)
        
        # Verify embeddings were called with full batch
        mock_embeddings.embed_documents.assert_called_once_with(texts)
        
        # Verify collection.add was called
        mock_collection.add.assert_called_once()

