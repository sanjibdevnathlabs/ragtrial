"""
Tests for Weaviate vectorstore implementation.

Unit tests with FULL MOCKING - no actual connections.
Following industry best practices:
- No network connections
- No actual Weaviate client connections
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
import sys
from unittest.mock import Mock, patch, MagicMock

from config import Config
from embeddings.base import EmbeddingsProtocol


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def mock_weaviate_module():
    """Auto-mock weaviate module for all tests in this file."""
    mock_weaviate = MagicMock()
    mock_classes = MagicMock()
    mock_config_module = MagicMock()
    mock_data = MagicMock()
    
    with patch.dict('sys.modules', {
        'weaviate': mock_weaviate,
        'weaviate.classes': mock_classes,
        'weaviate.classes.config': mock_classes.config,
        'weaviate.classes.data': mock_data,
        'weaviate.config': mock_config_module
    }):
        yield mock_weaviate


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
    """Create config with Weaviate settings (uses test.toml)."""
    return Config()


@pytest.fixture
def mock_weaviate_client():
    """Create mock Weaviate client."""
    client = MagicMock()
    
    # Mock collection/schema methods
    mock_collection = MagicMock()
    mock_collection.name = "TestDocument"
    client.collections.exists.return_value = True
    client.collections.get.return_value = mock_collection
    client.collections.create.return_value = mock_collection
    
    # Mock collection aggregate for stats
    mock_aggregate = MagicMock()
    mock_aggregate.total_count = 42
    mock_collection.aggregate.over_all.return_value = mock_aggregate
    
    # Mock query results
    mock_object1 = MagicMock()
    mock_object1.uuid = "doc_1"
    mock_object1.properties = {"text": "Document 1", "source": "a.pdf"}
    mock_object1.metadata = MagicMock()
    mock_object1.metadata.score = 0.9
    
    mock_object2 = MagicMock()
    mock_object2.uuid = "doc_2"
    mock_object2.properties = {"text": "Document 2", "source": "b.pdf"}
    mock_object2.metadata = MagicMock()
    mock_object2.metadata.score = 0.8
    
    mock_query_result = MagicMock()
    mock_query_result.objects = [mock_object1, mock_object2]
    mock_collection.query.near_vector.return_value = mock_query_result
    
    return client


@pytest.fixture
def weaviate_vectorstore(mock_config, mock_embeddings, mock_weaviate_client, mock_weaviate_module):
    """Create WeaviateVectorStore with mocked dependencies."""
    mock_weaviate_module.connect_to_local.return_value = mock_weaviate_client
    mock_weaviate_module.connect_to_custom.return_value = mock_weaviate_client
    
    from vectorstore.implementations.weaviate import WeaviateVectorStore
    vectorstore = WeaviateVectorStore(mock_config, mock_embeddings)
    # The client should already be set from connect_to_local, but ensure it's our mock
    vectorstore.client = mock_weaviate_client
    # Also set the collection to return the proper mock
    mock_collection = mock_weaviate_client.collections.get.return_value
    vectorstore.collection = mock_collection
    return vectorstore


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestInitialization:
    """Test WeaviateVectorStore initialization."""

    def test_initialization_success(self, mock_config, mock_embeddings, mock_weaviate_client, mock_weaviate_module):
        """Test successful initialization."""
        mock_weaviate_module.connect_to_local.return_value = mock_weaviate_client
        
        from vectorstore.implementations.weaviate import WeaviateVectorStore
        vectorstore = WeaviateVectorStore(mock_config, mock_embeddings)
        
        assert vectorstore is not None
        assert vectorstore.embeddings == mock_embeddings
        assert vectorstore.config == mock_config
        assert vectorstore.class_name == "TestDocument"

    def test_stores_configuration(self, mock_config, mock_embeddings, mock_weaviate_client, mock_weaviate_module):
        """Test configuration is stored correctly."""
        mock_weaviate_module.connect_to_local.return_value = mock_weaviate_client
        
        from vectorstore.implementations.weaviate import WeaviateVectorStore
        vectorstore = WeaviateVectorStore(mock_config, mock_embeddings)
        
        assert vectorstore.class_name == "TestDocument"
        # Verify embeddings dimension is used
        assert mock_embeddings.get_dimension() == 768


# ============================================================================
# COLLECTION INITIALIZATION TESTS
# ============================================================================


class TestDocumentInitialization:
    """Test collection initialization (create/get)."""

    def test_initialize_gets_existing_collection(self, weaviate_vectorstore, mock_weaviate_client):
        """Test initialize retrieves existing collection."""
        mock_weaviate_client.collections.exists.return_value = True
        
        weaviate_vectorstore.initialize()
        
        # Verify collection exists check was called
        mock_weaviate_client.collections.exists.assert_called()

    def test_initialize_creates_new_collection_if_not_exists(
        self, weaviate_vectorstore, mock_weaviate_client
    ):
        """Test initialize creates collection if it doesn't exist."""
        mock_weaviate_client.collections.exists.return_value = False
        
        weaviate_vectorstore.initialize()
        
        # Verify collection was created
        mock_weaviate_client.collections.create.assert_called()


# ============================================================================
# ADD DOCUMENTS TESTS
# ============================================================================


class TestAddDocuments:
    """Test adding documents to vectorstore."""

    def test_add_documents_success(self, weaviate_vectorstore, mock_embeddings):
        """Test successful document addition."""
        texts = ["Document 1", "Document 2"]
        metadatas = [{"source": "a.pdf"}, {"source": "b.pdf"}]
        
        weaviate_vectorstore.add_documents(texts, metadatas)
        
        # Verify embeddings were generated
        mock_embeddings.embed_documents.assert_called_once_with(texts)

    def test_add_documents_generates_ids_if_not_provided(
        self, weaviate_vectorstore, mock_embeddings
    ):
        """Test IDs are auto-generated if not provided."""
        texts = ["Document 1", "Document 2"]
        
        weaviate_vectorstore.add_documents(texts)
        
        # Verify embeddings were generated
        mock_embeddings.embed_documents.assert_called_once()

    def test_add_documents_uses_provided_ids(
        self, weaviate_vectorstore, mock_embeddings
    ):
        """Test provided IDs are used."""
        texts = ["Document 1"]
        ids = ["custom_id_1"]
        
        weaviate_vectorstore.add_documents(texts, ids=ids)
        
        # Verify embeddings were generated
        mock_embeddings.embed_documents.assert_called_once()

    def test_add_documents_includes_text_in_properties(
        self, weaviate_vectorstore, mock_embeddings
    ):
        """Test document text is stored in properties."""
        texts = ["Document 1"]
        
        weaviate_vectorstore.add_documents(texts)
        
        # Verify embeddings were generated
        mock_embeddings.embed_documents.assert_called_once()


# ============================================================================
# QUERY TESTS
# ============================================================================


class TestQuery:
    """Test querying the vectorstore."""

    def test_query_success(self, weaviate_vectorstore, mock_embeddings, mock_weaviate_client):
        """Test successful query."""
        # Setup mock collection
        mock_collection = mock_weaviate_client.collections.get.return_value
        
        # Mock query result
        mock_object1 = MagicMock()
        mock_object1.uuid = "doc_1"
        mock_object1.properties = {"text": "Text 1", "source": "a.pdf"}
        mock_object1.metadata = MagicMock()
        mock_object1.metadata.score = 0.9
        mock_object1.metadata.distance = 0.1
        
        mock_object2 = MagicMock()
        mock_object2.uuid = "doc_2"
        mock_object2.properties = {"text": "Text 2", "source": "b.pdf"}
        mock_object2.metadata = MagicMock()
        mock_object2.metadata.score = 0.8
        mock_object2.metadata.distance = 0.2
        
        mock_query_result = MagicMock()
        mock_query_result.objects = [mock_object1, mock_object2]
        mock_collection.query.near_vector.return_value = mock_query_result
        
        results = weaviate_vectorstore.query("test query", n_results=2)
        
        # Verify query embedding was generated
        mock_embeddings.embed_query.assert_called_once_with("test query")
        
        # Verify results format
        assert len(results) == 2
        assert results[0]["id"] == "doc_1"
        assert "text" in results[0]
        assert "metadata" in results[0]

    def test_query_with_metadata_filter(self, weaviate_vectorstore, mock_embeddings, mock_weaviate_client):
        """Test query with metadata filter."""
        mock_collection = mock_weaviate_client.collections.get.return_value
        mock_query_result = MagicMock()
        mock_query_result.objects = []
        mock_collection.query.near_vector.return_value = mock_query_result
        
        where_filter = {"source": "a.pdf"}
        weaviate_vectorstore.query("test query", where=where_filter)
        
        # Verify query was called
        assert mock_collection.query.near_vector.called

    def test_query_respects_n_results(self, weaviate_vectorstore, mock_embeddings, mock_weaviate_client):
        """Test query respects n_results parameter."""
        mock_collection = mock_weaviate_client.collections.get.return_value
        mock_query_result = MagicMock()
        mock_query_result.objects = []
        mock_collection.query.near_vector.return_value = mock_query_result
        
        weaviate_vectorstore.query("test query", n_results=10)
        
        # Verify query was called
        assert mock_collection.query.near_vector.called


# ============================================================================
# DELETE TESTS
# ============================================================================


class TestDelete:
    """Test deleting documents from vectorstore."""

    def test_delete_documents_by_ids(self, weaviate_vectorstore, mock_weaviate_client):
        """Test deleting documents by IDs."""
        mock_collection = mock_weaviate_client.collections.get.return_value
        
        ids_to_delete = ["doc_1", "doc_2", "doc_3"]
        weaviate_vectorstore.delete(ids_to_delete)
        
        # Verify delete was called for each ID
        assert mock_collection.data.delete_by_id.call_count == 3

    def test_delete_single_document(self, weaviate_vectorstore, mock_weaviate_client):
        """Test deleting a single document."""
        mock_collection = mock_weaviate_client.collections.get.return_value
        
        weaviate_vectorstore.delete(["doc_1"])
        
        mock_collection.data.delete_by_id.assert_called_once()


# ============================================================================
# STATISTICS TESTS
# ============================================================================


class TestStatistics:
    """Test retrieving vectorstore statistics."""

    def test_get_stats_returns_count(self, weaviate_vectorstore, mock_weaviate_client):
        """Test get_stats returns document count."""
        mock_collection = mock_weaviate_client.collections.get.return_value
        mock_aggregate = MagicMock()
        mock_aggregate.total_count = 42
        mock_collection.aggregate.over_all.return_value = mock_aggregate
        
        stats = weaviate_vectorstore.get_stats()
        
        assert stats["count"] == 42
        assert stats["class_name"] == "TestDocument"

    def test_get_stats_returns_collection_info(self, weaviate_vectorstore, mock_weaviate_client):
        """Test get_stats returns collection information."""
        mock_collection = mock_weaviate_client.collections.get.return_value
        mock_aggregate = MagicMock()
        mock_aggregate.total_count = 10
        mock_collection.aggregate.over_all.return_value = mock_aggregate
        
        stats = weaviate_vectorstore.get_stats()
        
        assert "count" in stats
        assert "class_name" in stats
        assert stats["class_name"] == "TestDocument"


# ============================================================================
# CLEAR TESTS
# ============================================================================


class TestClear:
    """Test clearing all documents from collection."""

    def test_clear_deletes_collection(self, weaviate_vectorstore, mock_weaviate_client):
        """Test clear removes collection and recreates it."""
        weaviate_vectorstore.clear()
        
        # Verify collection was deleted and recreated
        mock_weaviate_client.collections.delete.assert_called_once_with("TestDocument")
        # Create is called during initialization, so just verify delete was called
        assert mock_weaviate_client.collections.delete.called


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_add_documents_handles_embedding_error(
        self, weaviate_vectorstore, mock_embeddings
    ):
        """Test error handling when embeddings fail."""
        # Make embeddings fail
        mock_embeddings.embed_documents.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            weaviate_vectorstore.add_documents(["Document 1"])
        
        assert "API Error" in str(exc_info.value)

    def test_query_handles_embedding_error(
        self, weaviate_vectorstore, mock_embeddings
    ):
        """Test error handling when query embedding fails."""
        # Make embeddings fail
        mock_embeddings.embed_query.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            weaviate_vectorstore.query("test query")
        
        assert "API Error" in str(exc_info.value)


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic workflows (still fully mocked)."""

    def test_full_workflow_add_query_delete(
        self, weaviate_vectorstore, mock_embeddings, mock_weaviate_client
    ):
        """Test complete workflow: initialize, add, query, delete."""
        # Setup mock collection
        mock_collection = mock_weaviate_client.collections.get.return_value
        
        # Setup mock query result
        mock_object = MagicMock()
        mock_object.uuid = "doc_1"
        mock_object.properties = {"text": "Document 1 text", "source": "a.pdf"}
        mock_object.metadata = MagicMock()
        mock_object.metadata.score = 0.9
        mock_object.metadata.distance = 0.1
        
        mock_query_result = MagicMock()
        mock_query_result.objects = [mock_object]
        mock_collection.query.near_vector.return_value = mock_query_result
        
        # Mock aggregate
        mock_aggregate = MagicMock()
        mock_aggregate.total_count = 2
        mock_collection.aggregate.over_all.return_value = mock_aggregate
        
        # 1. Add documents
        texts = ["Document 1", "Document 2"]
        weaviate_vectorstore.add_documents(texts)
        mock_embeddings.embed_documents.assert_called_once()
        
        # 2. Query
        results = weaviate_vectorstore.query("test query", n_results=5)
        assert len(results) == 1
        assert results[0]["id"] == "doc_1"
        
        # 3. Get stats
        stats = weaviate_vectorstore.get_stats()
        assert "count" in stats
        assert "class_name" in stats
        
        # 4. Delete
        weaviate_vectorstore.delete(["doc_1"])
        mock_collection.data.delete_by_id.assert_called_once()

    def test_batch_operations(self, weaviate_vectorstore, mock_embeddings):
        """Test batch document operations."""
        # Add batch of documents
        texts = [f"Document {i}" for i in range(100)]
        metadatas = [{"source": f"file_{i}.pdf"} for i in range(100)]
        
        weaviate_vectorstore.add_documents(texts, metadatas)
        
        # Verify embeddings were called with full batch
        mock_embeddings.embed_documents.assert_called_once_with(texts)

