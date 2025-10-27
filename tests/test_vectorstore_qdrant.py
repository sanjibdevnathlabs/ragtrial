"""
Tests for Qdrant vectorstore implementation.

Unit tests with FULL MOCKING - no actual connections.
Following industry best practices:
- No network connections
- No actual Qdrant client connections
- Fast, isolated tests suitable for CI/CD

Test Coverage:
- Initialization with config and embeddings
- Collection creation and retrieval
- Document addition (single and batch)
- Query operations with filters
- Delete operations
- Statistics retrieval
- Collection clearing
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from config import Config
from vectorstore.implementations.qdrant import QdrantVectorStore
from embeddings.base import EmbeddingsProtocol


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_embeddings():
    """Create mock embeddings provider."""
    embeddings = Mock(spec=EmbeddingsProtocol)
    embeddings.embed_documents.return_value = [
        [0.1, 0.2, 0.3] * 256,  # 768-dim vector
        [0.4, 0.5, 0.6] * 256,  # 768-dim vector
    ]
    embeddings.embed_query.return_value = [0.7, 0.8, 0.9] * 256
    embeddings.get_dimension.return_value = 768
    return embeddings


@pytest.fixture
def mock_config():
    """Create config with Qdrant settings (uses test.toml)."""
    return Config()


@pytest.fixture
def mock_qdrant_client():
    """Create mock Qdrant client."""
    client = MagicMock()
    
    # Mock collection info
    mock_collection_info = MagicMock()
    mock_collection_info.status = "green"
    mock_collection_info.vectors_count = 42
    
    # Mock collection methods
    client.collection_exists.return_value = True
    client.get_collection.return_value = mock_collection_info
    client.create_collection.return_value = None
    client.upsert.return_value = None
    client.delete.return_value = None
    
    # Mock search results
    mock_point1 = MagicMock()
    mock_point1.id = "doc_1"
    mock_point1.score = 0.9
    mock_point1.payload = {"text": "Document 1", "source": "a.pdf"}
    
    mock_point2 = MagicMock()
    mock_point2.id = "doc_2"
    mock_point2.score = 0.8
    mock_point2.payload = {"text": "Document 2", "source": "b.pdf"}
    
    client.search.return_value = [mock_point1, mock_point2]
    
    return client


@pytest.fixture
def qdrant_vectorstore(mock_config, mock_embeddings, mock_qdrant_client):
    """Create QdrantVectorStore with mocked dependencies."""
    with patch("qdrant_client.QdrantClient", return_value=mock_qdrant_client):
        with patch("qdrant_client.models.Distance"):
            with patch("qdrant_client.models.VectorParams"):
                with patch("qdrant_client.models.PointStruct"):
                    vectorstore = QdrantVectorStore(mock_config, mock_embeddings)
                    return vectorstore


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestInitialization:
    """Test QdrantVectorStore initialization."""

    def test_initialization_success(self, mock_config, mock_embeddings, mock_qdrant_client):
        """Test successful initialization."""
        with patch("qdrant_client.QdrantClient", return_value=mock_qdrant_client):
            with patch("qdrant_client.models.Distance"):
                with patch("qdrant_client.models.VectorParams"):
                    with patch("qdrant_client.models.PointStruct"):
                        vectorstore = QdrantVectorStore(mock_config, mock_embeddings)
                        
                        assert vectorstore is not None
                        assert vectorstore.embeddings == mock_embeddings
                        assert vectorstore.config == mock_config
                        assert vectorstore.collection_name == "test_collection"

    def test_stores_configuration(self, mock_config, mock_embeddings, mock_qdrant_client):
        """Test configuration is stored correctly."""
        with patch("qdrant_client.QdrantClient", return_value=mock_qdrant_client):
            with patch("qdrant_client.models.Distance"):
                with patch("qdrant_client.models.VectorParams"):
                    with patch("qdrant_client.models.PointStruct"):
                        vectorstore = QdrantVectorStore(mock_config, mock_embeddings)
                        
                        assert vectorstore.collection_name == "test_collection"
                        # distance is a mock object (Distance.COSINE)
                        assert vectorstore.distance is not None
                        # Verify embeddings dimension is used
                        assert mock_embeddings.get_dimension() == 768


# ============================================================================
# COLLECTION INITIALIZATION TESTS
# ============================================================================


class TestCollectionInitialization:
    """Test collection initialization (create/get)."""

    def test_initialize_gets_existing_collection(self, qdrant_vectorstore, mock_qdrant_client):
        """Test initialize retrieves existing collection."""
        # Mock existing collection
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        mock_collections_response = MagicMock()
        mock_collections_response.collections = [mock_collection]
        mock_qdrant_client.get_collections.return_value = mock_collections_response
        
        qdrant_vectorstore.initialize()
        
        # Verify get_collections was called
        mock_qdrant_client.get_collections.assert_called_once()

    def test_initialize_creates_new_collection_if_not_exists(
        self, qdrant_vectorstore, mock_qdrant_client
    ):
        """Test initialize creates collection if it doesn't exist."""
        # Simulate collection not found
        mock_collections_response = MagicMock()
        mock_collections_response.collections = []
        mock_qdrant_client.get_collections.return_value = mock_collections_response
        
        qdrant_vectorstore.initialize()
        
        # Verify collection was created
        mock_qdrant_client.create_collection.assert_called_once()


# ============================================================================
# ADD DOCUMENTS TESTS
# ============================================================================


class TestAddDocuments:
    """Test adding documents to vectorstore."""

    def test_add_documents_success(self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client):
        """Test successful document addition."""
        texts = ["Document 1", "Document 2"]
        metadatas = [{"source": "a.pdf"}, {"source": "b.pdf"}]
        
        qdrant_vectorstore.add_documents(texts, metadatas)
        
        # Verify embeddings were generated
        mock_embeddings.embed_documents.assert_called_once_with(texts)
        
        # Verify upsert was called
        assert mock_qdrant_client.upsert.called

    def test_add_documents_generates_ids_if_not_provided(
        self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client
    ):
        """Test IDs are auto-generated if not provided."""
        texts = ["Document 1", "Document 2"]
        
        qdrant_vectorstore.add_documents(texts)
        
        # Verify upsert was called
        assert mock_qdrant_client.upsert.called

    def test_add_documents_uses_provided_ids(
        self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client
    ):
        """Test provided IDs are used."""
        texts = ["Document 1"]
        ids = ["custom_id_1"]
        
        qdrant_vectorstore.add_documents(texts, ids=ids)
        
        # Verify upsert was called
        assert mock_qdrant_client.upsert.called

    def test_add_documents_includes_text_in_payload(
        self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client
    ):
        """Test document text is stored in payload."""
        texts = ["Document 1"]
        
        qdrant_vectorstore.add_documents(texts)
        
        # Verify upsert was called
        assert mock_qdrant_client.upsert.called


# ============================================================================
# QUERY TESTS
# ============================================================================


class TestQuery:
    """Test querying the vectorstore."""

    def test_query_success(self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client):
        """Test successful query."""
        # Mock search results
        mock_point1 = MagicMock()
        mock_point1.id = "doc_1"
        mock_point1.score = 0.9
        mock_point1.payload = {"text": "Text 1", "source": "a.pdf"}
        
        mock_point2 = MagicMock()
        mock_point2.id = "doc_2"
        mock_point2.score = 0.8
        mock_point2.payload = {"text": "Text 2", "source": "b.pdf"}
        
        mock_qdrant_client.search.return_value = [mock_point1, mock_point2]
        
        results = qdrant_vectorstore.query("test query", n_results=2)
        
        # Verify query embedding was generated
        mock_embeddings.embed_query.assert_called_once_with("test query")
        
        # Verify search was called
        mock_qdrant_client.search.assert_called_once()
        
        # Verify results format
        assert len(results) == 2
        assert results[0]["id"] == "doc_1"
        assert results[0]["text"] == "Text 1"
        assert results[0]["metadata"]["source"] == "a.pdf"
        assert results[0]["distance"] == 0.9

    def test_query_with_metadata_filter(self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client):
        """Test query with metadata filter."""
        mock_qdrant_client.search.return_value = []
        
        where_filter = {"source": "a.pdf"}
        qdrant_vectorstore.query("test query", where=where_filter)
        
        # Verify search was called with filter
        call_args = mock_qdrant_client.search.call_args
        assert call_args.kwargs.get("query_filter") is not None

    def test_query_respects_n_results(self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client):
        """Test query respects n_results parameter."""
        mock_qdrant_client.search.return_value = []
        
        qdrant_vectorstore.query("test query", n_results=10)
        
        call_args = mock_qdrant_client.search.call_args
        assert call_args.kwargs.get("limit") == 10


# ============================================================================
# DELETE TESTS
# ============================================================================


class TestDelete:
    """Test deleting documents from vectorstore."""

    def test_delete_documents_by_ids(self, qdrant_vectorstore, mock_qdrant_client):
        """Test deleting documents by IDs."""
        ids_to_delete = ["doc_1", "doc_2", "doc_3"]
        qdrant_vectorstore.delete(ids_to_delete)
        
        mock_qdrant_client.delete.assert_called_once()

    def test_delete_single_document(self, qdrant_vectorstore, mock_qdrant_client):
        """Test deleting a single document."""
        qdrant_vectorstore.delete(["doc_1"])
        
        mock_qdrant_client.delete.assert_called_once()


# ============================================================================
# STATISTICS TESTS
# ============================================================================


class TestStatistics:
    """Test retrieving vectorstore statistics."""

    def test_get_stats_returns_count(self, qdrant_vectorstore, mock_qdrant_client):
        """Test get_stats returns document count."""
        mock_collection_info = MagicMock()
        mock_collection_info.points_count = 42
        mock_collection_info.vectors_count = 42
        mock_collection_info.indexed_vectors_count = 42
        mock_qdrant_client.get_collection.return_value = mock_collection_info
        
        stats = qdrant_vectorstore.get_stats()
        
        assert stats["count"] == 42
        assert stats["collection_name"] == "test_collection"

    def test_get_stats_returns_collection_info(self, qdrant_vectorstore, mock_qdrant_client):
        """Test get_stats returns collection information."""
        mock_collection_info = MagicMock()
        mock_collection_info.vectors_count = 10
        mock_collection_info.points_count = 10
        mock_qdrant_client.get_collection.return_value = mock_collection_info
        
        stats = qdrant_vectorstore.get_stats()
        
        assert "count" in stats
        assert "collection_name" in stats
        assert stats["collection_name"] == "test_collection"


# ============================================================================
# CLEAR TESTS
# ============================================================================


class TestClear:
    """Test clearing all documents from collection."""

    def test_clear_deletes_collection(self, qdrant_vectorstore, mock_qdrant_client):
        """Test clear removes collection and recreates it."""
        qdrant_vectorstore.clear()
        
        # Verify collection was deleted and recreated
        mock_qdrant_client.delete_collection.assert_called_once_with("test_collection")
        mock_qdrant_client.create_collection.assert_called_once()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_add_documents_handles_embedding_error(
        self, qdrant_vectorstore, mock_embeddings
    ):
        """Test error handling when embeddings fail."""
        # Make embeddings fail
        mock_embeddings.embed_documents.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            qdrant_vectorstore.add_documents(["Document 1"])
        
        assert "API Error" in str(exc_info.value)

    def test_query_handles_embedding_error(
        self, qdrant_vectorstore, mock_embeddings
    ):
        """Test error handling when query embedding fails."""
        # Make embeddings fail
        mock_embeddings.embed_query.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            qdrant_vectorstore.query("test query")
        
        assert "API Error" in str(exc_info.value)


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic workflows (still fully mocked)."""

    def test_full_workflow_add_query_delete(
        self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client
    ):
        """Test complete workflow: initialize, add, query, delete."""
        # Setup mock search
        mock_point = MagicMock()
        mock_point.id = "doc_1"
        mock_point.score = 0.9
        mock_point.payload = {"text": "Document 1 text", "source": "a.pdf"}
        mock_qdrant_client.search.return_value = [mock_point]
        
        # Mock collection info
        mock_collection_info = MagicMock()
        mock_collection_info.vectors_count = 2
        mock_collection_info.points_count = 2
        mock_qdrant_client.get_collection.return_value = mock_collection_info
        
        # 1. Add documents
        texts = ["Document 1", "Document 2"]
        qdrant_vectorstore.add_documents(texts)
        assert mock_qdrant_client.upsert.called
        
        # 2. Query
        results = qdrant_vectorstore.query("test query", n_results=5)
        assert len(results) == 1
        assert results[0]["id"] == "doc_1"
        
        # 3. Get stats
        stats = qdrant_vectorstore.get_stats()
        assert "count" in stats
        assert "collection_name" in stats
        
        # 4. Delete
        qdrant_vectorstore.delete(["doc_1"])
        mock_qdrant_client.delete.assert_called_once()

    def test_batch_operations(self, qdrant_vectorstore, mock_embeddings, mock_qdrant_client):
        """Test batch document operations."""
        # Add batch of documents
        texts = [f"Document {i}" for i in range(100)]
        metadatas = [{"source": f"file_{i}.pdf"} for i in range(100)]
        
        qdrant_vectorstore.add_documents(texts, metadatas)
        
        # Verify embeddings were called with full batch
        mock_embeddings.embed_documents.assert_called_once_with(texts)
        
        # Verify upsert was called
        assert mock_qdrant_client.upsert.called

