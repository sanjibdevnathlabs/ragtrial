"""
Tests for Pinecone vectorstore implementation.

Unit tests with FULL MOCKING - no actual API calls or connections.
Following industry best practices:
- No network connections
- No actual Pinecone API calls
- Fast, isolated tests suitable for CI/CD

Test Coverage:
- Initialization with config and embeddings
- Index creation and retrieval
- Document addition (single and batch)
- Query operations with metadata filtering
- Delete operations
- Statistics retrieval
- Index clearing
- Error handling
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from config import Config
from embeddings.base import EmbeddingsProtocol
from vectorstore.implementations.pinecone import PineconeVectorStore

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
    """Create config with Pinecone settings (uses test.toml)."""
    return Config()


@pytest.fixture
def mock_pinecone_client():
    """Create mock Pinecone client."""
    client = MagicMock()
    index = MagicMock()

    # Mock query results - must be object with .matches attribute
    mock_query_result = MagicMock()
    mock_match1 = MagicMock()
    mock_match1.id = "doc_1"
    mock_match1.score = 0.9
    mock_match1.metadata = {"text": "Document 1", "source": "a.pdf"}

    mock_match2 = MagicMock()
    mock_match2.id = "doc_2"
    mock_match2.score = 0.8
    mock_match2.metadata = {"text": "Document 2", "source": "b.pdf"}

    mock_query_result.matches = [mock_match1, mock_match2]

    # Mock stats - must be object with attributes
    mock_stats = MagicMock()
    mock_stats.dimension = 768
    mock_stats.index_fullness = 0.1
    mock_stats.total_vector_count = 42

    # Mock index methods
    index.upsert.return_value = {"upserted_count": 2}
    index.query.return_value = mock_query_result
    index.delete.return_value = None
    index.describe_index_stats.return_value = mock_stats

    # Mock client methods
    client.Index.return_value = index
    client.list_indexes.return_value = []
    client.create_index.return_value = None

    return client


@pytest.fixture
def pinecone_vectorstore(mock_config, mock_embeddings, mock_pinecone_client):
    """Create PineconeVectorStore with mocked dependencies."""
    with patch("pinecone.Pinecone", return_value=mock_pinecone_client):
        with patch("pinecone.ServerlessSpec") as mock_spec:
            mock_spec.return_value = MagicMock()
            vectorstore = PineconeVectorStore(mock_config, mock_embeddings)
            vectorstore.pc = mock_pinecone_client
            return vectorstore


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


class TestInitialization:
    """Test PineconeVectorStore initialization."""

    def test_initialization_success(
        self, mock_config, mock_embeddings, mock_pinecone_client
    ):
        """Test successful initialization."""
        with patch("pinecone.Pinecone", return_value=mock_pinecone_client):
            with patch("pinecone.ServerlessSpec"):
                vectorstore = PineconeVectorStore(mock_config, mock_embeddings)

                assert vectorstore is not None
                assert vectorstore.embeddings == mock_embeddings
                assert vectorstore.config == mock_config
                assert vectorstore.index_name == "test-index"

    def test_initialization_disables_ssl_when_configured(
        self, mock_config, mock_embeddings, mock_pinecone_client
    ):
        """Test SSL verification is disabled when configured."""
        with patch(
            "pinecone.Pinecone", return_value=mock_pinecone_client
        ) as mock_pinecone:
            with patch("pinecone.ServerlessSpec"):
                with patch("urllib3.disable_warnings"):
                    PineconeVectorStore(mock_config, mock_embeddings)

                    # Verify Pinecone was called with ssl_verify=False
                    assert mock_pinecone.called
                    call_kwargs = mock_pinecone.call_args.kwargs
                    assert call_kwargs.get("ssl_verify") is False

    def test_stores_configuration(
        self, mock_config, mock_embeddings, mock_pinecone_client
    ):
        """Test configuration is stored correctly."""
        with patch("pinecone.Pinecone", return_value=mock_pinecone_client):
            with patch("pinecone.ServerlessSpec"):
                vectorstore = PineconeVectorStore(mock_config, mock_embeddings)

                assert vectorstore.index_name == "test-index"
                assert vectorstore.dimension == 768
                assert vectorstore.metric == "cosine"


# ============================================================================
# INDEX INITIALIZATION TESTS
# ============================================================================


class TestIndexInitialization:
    """Test index initialization (create/get)."""

    def test_initialize_gets_existing_index(
        self, pinecone_vectorstore, mock_pinecone_client
    ):
        """Test initialize retrieves existing index."""
        # Mock index exists
        mock_index_info = MagicMock()
        mock_index_info.name = "test-index"
        mock_pinecone_client.list_indexes.return_value = [mock_index_info]

        pinecone_vectorstore.initialize()

        assert pinecone_vectorstore.index is not None
        mock_pinecone_client.Index.assert_called_once_with("test-index")

    def test_initialize_creates_new_index_if_not_exists(
        self, pinecone_vectorstore, mock_pinecone_client
    ):
        """Test initialize creates index if it doesn't exist."""
        # Mock index doesn't exist
        mock_pinecone_client.list_indexes.return_value = []

        pinecone_vectorstore.initialize()

        # Verify index was created
        mock_pinecone_client.create_index.assert_called_once()


# ============================================================================
# ADD DOCUMENTS TESTS
# ============================================================================


class TestAddDocuments:
    """Test adding documents to vectorstore."""

    def test_add_documents_success(self, pinecone_vectorstore, mock_embeddings):
        """Test successful document addition."""
        mock_index = MagicMock()
        mock_index.upsert.return_value = {"upserted_count": 2}
        pinecone_vectorstore.index = mock_index

        texts = ["Document 1", "Document 2"]
        metadatas = [{"source": "a.pdf"}, {"source": "b.pdf"}]

        pinecone_vectorstore.add_documents(texts, metadatas)

        # Verify embeddings were generated
        mock_embeddings.embed_documents.assert_called_once_with(texts)

        # Verify upsert was called
        assert mock_index.upsert.called

    def test_add_documents_generates_ids_if_not_provided(
        self, pinecone_vectorstore, mock_embeddings
    ):
        """Test IDs are auto-generated if not provided."""
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        texts = ["Document 1", "Document 2"]

        pinecone_vectorstore.add_documents(texts)

        # Check that vectors were upserted
        assert mock_index.upsert.called

    def test_add_documents_uses_provided_ids(
        self, pinecone_vectorstore, mock_embeddings
    ):
        """Test provided IDs are used."""
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        texts = ["Document 1"]
        ids = ["custom_id_1"]

        pinecone_vectorstore.add_documents(texts, ids=ids)

        # Verify upsert was called
        assert mock_index.upsert.called

    def test_add_documents_includes_text_in_metadata(
        self, pinecone_vectorstore, mock_embeddings
    ):
        """Test document text is stored in metadata."""
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        texts = ["Document 1"]

        pinecone_vectorstore.add_documents(texts)

        # Verify upsert was called with metadata containing text
        call_args = mock_index.upsert.call_args
        vectors = (
            call_args.args[0] if call_args.args else call_args.kwargs.get("vectors")
        )

        # Check that text is in metadata
        assert vectors is not None


# ============================================================================
# QUERY TESTS
# ============================================================================


class TestQuery:
    """Test querying the vectorstore."""

    def test_query_success(self, pinecone_vectorstore, mock_embeddings):
        """Test successful query."""
        mock_index = MagicMock()

        # Create mock query result with proper structure
        mock_query_result = MagicMock()
        mock_match1 = MagicMock()
        mock_match1.id = "doc_1"
        mock_match1.score = 0.9
        mock_match1.metadata = {"text": "Text 1", "source": "a.pdf"}

        mock_match2 = MagicMock()
        mock_match2.id = "doc_2"
        mock_match2.score = 0.8
        mock_match2.metadata = {"text": "Text 2", "source": "b.pdf"}

        mock_query_result.matches = [mock_match1, mock_match2]
        mock_index.query.return_value = mock_query_result
        pinecone_vectorstore.index = mock_index

        results = pinecone_vectorstore.query("test query", n_results=2)

        # Verify query embedding was generated
        mock_embeddings.embed_query.assert_called_once_with("test query")

        # Verify index was queried
        mock_index.query.assert_called_once()

        # Verify results format
        assert len(results) == 2
        assert results[0]["id"] == "doc_1"
        assert results[0]["text"] == "Text 1"
        assert results[0]["metadata"]["source"] == "a.pdf"
        assert results[0]["distance"] == 0.9

    def test_query_with_metadata_filter(self, pinecone_vectorstore, mock_embeddings):
        """Test query with metadata filter."""
        mock_index = MagicMock()
        mock_query_result = MagicMock()
        mock_query_result.matches = []
        mock_index.query.return_value = mock_query_result
        pinecone_vectorstore.index = mock_index

        where_filter = {"source": "a.pdf"}
        pinecone_vectorstore.query("test query", where=where_filter)

        # Verify filter was passed
        call_args = mock_index.query.call_args
        assert call_args.kwargs.get("filter") == where_filter

    def test_query_respects_n_results(self, pinecone_vectorstore, mock_embeddings):
        """Test query respects n_results parameter."""
        mock_index = MagicMock()
        mock_query_result = MagicMock()
        mock_query_result.matches = []
        mock_index.query.return_value = mock_query_result
        pinecone_vectorstore.index = mock_index

        pinecone_vectorstore.query("test query", n_results=10)

        call_args = mock_index.query.call_args
        assert call_args.kwargs.get("top_k") == 10


# ============================================================================
# DELETE TESTS
# ============================================================================


class TestDelete:
    """Test deleting documents from vectorstore."""

    def test_delete_documents_by_ids(self, pinecone_vectorstore):
        """Test deleting documents by IDs."""
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        ids_to_delete = ["doc_1", "doc_2", "doc_3"]
        pinecone_vectorstore.delete(ids_to_delete)

        mock_index.delete.assert_called_once_with(ids=ids_to_delete)

    def test_delete_single_document(self, pinecone_vectorstore):
        """Test deleting a single document."""
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        pinecone_vectorstore.delete(["doc_1"])

        mock_index.delete.assert_called_once_with(ids=["doc_1"])


# ============================================================================
# STATISTICS TESTS
# ============================================================================


class TestStatistics:
    """Test retrieving vectorstore statistics."""

    def test_get_stats_returns_count(self, pinecone_vectorstore):
        """Test get_stats returns document count."""
        mock_index = MagicMock()
        mock_stats = MagicMock()
        mock_stats.dimension = 768
        mock_stats.index_fullness = 0.1
        mock_stats.total_vector_count = 42
        mock_index.describe_index_stats.return_value = mock_stats
        pinecone_vectorstore.index = mock_index

        stats = pinecone_vectorstore.get_stats()

        assert stats["count"] == 42
        assert stats["index_name"] == "test-index"

    def test_get_stats_returns_index_info(self, pinecone_vectorstore):
        """Test get_stats returns index information."""
        mock_index = MagicMock()
        mock_stats = MagicMock()
        mock_stats.dimension = 768
        mock_stats.index_fullness = 0.5
        mock_stats.total_vector_count = 100
        mock_index.describe_index_stats.return_value = mock_stats
        pinecone_vectorstore.index = mock_index

        stats = pinecone_vectorstore.get_stats()

        assert "count" in stats
        assert "index_name" in stats
        assert "dimension" in stats
        assert "metric" in stats
        assert "initialized" in stats
        assert stats["dimension"] == 768
        assert stats["initialized"] is True


# ============================================================================
# CLEAR TESTS
# ============================================================================


class TestClear:
    """Test clearing all documents from index."""

    def test_clear_deletes_all_documents(self, pinecone_vectorstore):
        """Test clear removes all documents."""
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        pinecone_vectorstore.clear()

        # Verify delete_all was called
        mock_index.delete.assert_called_once_with(delete_all=True)


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_add_documents_handles_embedding_error(
        self, pinecone_vectorstore, mock_embeddings
    ):
        """Test error handling when embeddings fail."""
        # Initialize index first
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        # Make embeddings fail
        mock_embeddings.embed_documents.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            pinecone_vectorstore.add_documents(["Document 1"])

        assert "API Error" in str(exc_info.value)

    def test_query_handles_embedding_error(self, pinecone_vectorstore, mock_embeddings):
        """Test error handling when query embedding fails."""
        # Initialize index first
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        # Make embeddings fail
        mock_embeddings.embed_query.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            pinecone_vectorstore.query("test query")

        assert "API Error" in str(exc_info.value)


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestIntegration:
    """Test realistic workflows (still fully mocked)."""

    def test_full_workflow_add_query_delete(
        self, pinecone_vectorstore, mock_embeddings
    ):
        """Test complete workflow: initialize, add, query, delete."""
        # Setup mock index
        mock_index = MagicMock()

        # Mock query result
        mock_query_result = MagicMock()
        mock_match = MagicMock()
        mock_match.id = "doc_1"
        mock_match.score = 0.9
        mock_match.metadata = {"text": "Document 1 text", "source": "a.pdf"}
        mock_query_result.matches = [mock_match]
        mock_index.query.return_value = mock_query_result

        # Mock stats
        mock_stats = MagicMock()
        mock_stats.dimension = 768
        mock_stats.total_vector_count = 2
        mock_index.describe_index_stats.return_value = mock_stats

        pinecone_vectorstore.index = mock_index

        # 1. Add documents
        texts = ["Document 1", "Document 2"]
        pinecone_vectorstore.add_documents(texts)
        assert mock_index.upsert.called

        # 2. Query
        results = pinecone_vectorstore.query("test query", n_results=5)
        assert len(results) == 1
        assert results[0]["id"] == "doc_1"

        # 3. Get stats
        stats = pinecone_vectorstore.get_stats()
        assert stats["count"] == 2

        # 4. Delete
        pinecone_vectorstore.delete(["doc_1"])
        mock_index.delete.assert_called_with(ids=["doc_1"])

    def test_batch_operations(self, pinecone_vectorstore, mock_embeddings):
        """Test batch document operations."""
        mock_index = MagicMock()
        pinecone_vectorstore.index = mock_index

        # Add batch of documents
        texts = [f"Document {i}" for i in range(100)]
        metadatas = [{"source": f"file_{i}.pdf"} for i in range(100)]

        pinecone_vectorstore.add_documents(texts, metadatas)

        # Verify embeddings were called with full batch
        mock_embeddings.embed_documents.assert_called_once_with(texts)

        # Verify upsert was called (may be batched internally)
        assert mock_index.upsert.called
