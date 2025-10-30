"""
Tests for vectorstore factory.

Unit tests with FULL MOCKING - no actual database connections.
Following industry best practices:
- No database connections
- No network access
- Fast, isolated tests suitable for CI/CD

Test Coverage:
- Factory provider creation for all supported providers (MOCKED)
- Error handling for invalid providers
- Configuration loading and validation
- Provider type verification
- Embeddings integration
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from config import Config
from embeddings.base import EmbeddingsProtocol
from vectorstore import create_vectorstore

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_embeddings():
    """Create mock embeddings provider (duck-typed protocol)."""
    embeddings = Mock(spec=EmbeddingsProtocol)
    embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    embeddings.embed_query.return_value = [0.4, 0.5, 0.6]
    embeddings.get_dimension.return_value = 768
    return embeddings


@pytest.fixture
def config_chroma():
    """Create config with Chroma provider (using test.toml)."""
    config = Config()
    config.vectorstore.provider = "chroma"
    return config


@pytest.fixture
def config_pinecone():
    """Create config with Pinecone provider (using test.toml)."""
    config = Config()
    config.vectorstore.provider = "pinecone"
    return config


@pytest.fixture
def config_qdrant():
    """Create config with Qdrant provider (using test.toml)."""
    config = Config()
    config.vectorstore.provider = "qdrant"
    return config


@pytest.fixture
def config_weaviate():
    """Create config with Weaviate provider (using test.toml)."""
    config = Config()
    config.vectorstore.provider = "weaviate"
    return config


@pytest.fixture
def config_invalid():
    """Create config with invalid provider (using test.toml)."""
    config = Config()
    config.vectorstore.provider = "invalid_provider"
    return config


# ============================================================================
# FACTORY TESTS - Provider Creation (MOCKED)
# ============================================================================


class TestVectorStoreFactory:
    """Test vectorstore factory creation with mocked providers."""

    def test_create_chroma_vectorstore(self, config_chroma, mock_embeddings):
        """Test creating Chroma vectorstore provider (MOCKED)."""
        with patch("chromadb.PersistentClient"):
            with patch("pathlib.Path.mkdir"):
                vectorstore = create_vectorstore(config_chroma, mock_embeddings)

                assert vectorstore is not None
                # Protocol duck typing - check for required methods
                assert hasattr(vectorstore, "initialize")
                assert hasattr(vectorstore, "add_documents")
                assert hasattr(vectorstore, "query")
                assert hasattr(vectorstore, "delete")
                assert hasattr(vectorstore, "get_stats")
                assert hasattr(vectorstore, "clear")
                assert callable(vectorstore.initialize)
                assert callable(vectorstore.add_documents)
                assert callable(vectorstore.query)

    def test_create_pinecone_vectorstore(self, config_pinecone, mock_embeddings):
        """Test creating Pinecone vectorstore provider (MOCKED)."""
        with patch("pinecone.Pinecone"):
            vectorstore = create_vectorstore(config_pinecone, mock_embeddings)

            assert vectorstore is not None
            # Protocol duck typing - check for required methods
            assert hasattr(vectorstore, "initialize")
            assert hasattr(vectorstore, "add_documents")
            assert hasattr(vectorstore, "query")
            assert hasattr(vectorstore, "delete")
            assert hasattr(vectorstore, "get_stats")
            assert hasattr(vectorstore, "clear")

    def test_create_qdrant_vectorstore(self, config_qdrant, mock_embeddings):
        """Test creating Qdrant vectorstore provider (MOCKED)."""
        with patch("qdrant_client.QdrantClient"):
            vectorstore = create_vectorstore(config_qdrant, mock_embeddings)

            assert vectorstore is not None
            # Protocol duck typing - check for required methods
            assert hasattr(vectorstore, "initialize")
            assert hasattr(vectorstore, "add_documents")
            assert hasattr(vectorstore, "query")
            assert hasattr(vectorstore, "delete")
            assert hasattr(vectorstore, "get_stats")
            assert hasattr(vectorstore, "clear")

    def test_create_weaviate_vectorstore(self, config_weaviate, mock_embeddings):
        """Test creating Weaviate vectorstore provider (MOCKED)."""
        with patch("weaviate.connect_to_custom") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            vectorstore = create_vectorstore(config_weaviate, mock_embeddings)

            assert vectorstore is not None
            # Protocol duck typing - check for required methods
            assert hasattr(vectorstore, "initialize")
            assert hasattr(vectorstore, "add_documents")
            assert hasattr(vectorstore, "query")
            assert hasattr(vectorstore, "delete")
            assert hasattr(vectorstore, "get_stats")
            assert hasattr(vectorstore, "clear")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling in factory."""

    def test_invalid_provider_raises_error(self, config_invalid, mock_embeddings):
        """Test factory raises error for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            create_vectorstore(config_invalid, mock_embeddings)

        assert "Unknown vectorstore provider" in str(exc_info.value)
        assert "invalid_provider" in str(exc_info.value)

    def test_factory_validates_provider_name(self, config_invalid, mock_embeddings):
        """Test factory validates provider names."""
        with pytest.raises(ValueError):
            create_vectorstore(config_invalid, mock_embeddings)


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================


class TestConfiguration:
    """Test configuration handling in factory."""

    def test_factory_uses_config_provider(self, config_chroma, mock_embeddings):
        """Test factory uses provider from config."""
        with patch("chromadb.PersistentClient"):
            with patch("pathlib.Path.mkdir"):
                vectorstore = create_vectorstore(config_chroma, mock_embeddings)
                assert vectorstore is not None

    def test_factory_respects_provider_switching(self, config_chroma, mock_embeddings):
        """Test factory respects provider changes."""
        # First provider
        with patch("chromadb.PersistentClient"):
            with patch("pathlib.Path.mkdir"):
                vectorstore1 = create_vectorstore(config_chroma, mock_embeddings)
                assert vectorstore1 is not None

        # Switch provider
        config_chroma.vectorstore.provider = "pinecone"
        with patch("pinecone.Pinecone"):
            vectorstore2 = create_vectorstore(config_chroma, mock_embeddings)
            assert vectorstore2 is not None

        # Different provider instances
        assert type(vectorstore1).__name__ != type(vectorstore2).__name__

    def test_factory_receives_embeddings(self, config_chroma, mock_embeddings):
        """Test factory receives and passes embeddings to provider."""
        with patch("chromadb.Client"):
            vectorstore = create_vectorstore(config_chroma, mock_embeddings)
            # Vectorstore should have reference to embeddings
            assert hasattr(vectorstore, "embeddings")


# ============================================================================
# PROVIDER VERIFICATION TESTS
# ============================================================================


class TestProviderTypes:
    """Test correct provider types are returned."""

    def test_chroma_provider_type(self, config_chroma, mock_embeddings):
        """Test Chroma provider returns correct type."""
        with patch("chromadb.PersistentClient"):
            with patch("pathlib.Path.mkdir"):
                vectorstore = create_vectorstore(config_chroma, mock_embeddings)
                assert type(vectorstore).__name__ == "ChromaVectorStore"

    def test_pinecone_provider_type(self, config_pinecone, mock_embeddings):
        """Test Pinecone provider returns correct type."""
        with patch("pinecone.Pinecone"):
            vectorstore = create_vectorstore(config_pinecone, mock_embeddings)
            assert type(vectorstore).__name__ == "PineconeVectorStore"

    def test_qdrant_provider_type(self, config_qdrant, mock_embeddings):
        """Test Qdrant provider returns correct type."""
        with patch("qdrant_client.QdrantClient"):
            vectorstore = create_vectorstore(config_qdrant, mock_embeddings)
            assert type(vectorstore).__name__ == "QdrantVectorStore"

    def test_weaviate_provider_type(self, config_weaviate, mock_embeddings):
        """Test Weaviate provider returns correct type."""
        with patch("weaviate.connect_to_custom") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            vectorstore = create_vectorstore(config_weaviate, mock_embeddings)
            assert type(vectorstore).__name__ == "WeaviateVectorStore"


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestFactoryIntegration:
    """Test factory in realistic scenarios (still mocked)."""

    def test_factory_with_all_providers_sequentially(self, mock_embeddings):
        """Test factory can create all providers in sequence by switching providers."""
        config = Config()
        providers_created = []

        # Chroma
        config.vectorstore.provider = "chroma"
        with patch("chromadb.Client"):
            chroma_vs = create_vectorstore(config, mock_embeddings)
            providers_created.append(type(chroma_vs).__name__)

        # Pinecone
        config.vectorstore.provider = "pinecone"
        with patch("pinecone.Pinecone"):
            pinecone_vs = create_vectorstore(config, mock_embeddings)
            providers_created.append(type(pinecone_vs).__name__)

        # Qdrant
        config.vectorstore.provider = "qdrant"
        with patch("qdrant_client.QdrantClient"):
            qdrant_vs = create_vectorstore(config, mock_embeddings)
            providers_created.append(type(qdrant_vs).__name__)

        # Weaviate
        config.vectorstore.provider = "weaviate"
        with patch("weaviate.connect_to_custom") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client
            weaviate_vs = create_vectorstore(config, mock_embeddings)
            providers_created.append(type(weaviate_vs).__name__)

        # Verify all 4 providers were created
        assert len(providers_created) == 4
        assert "ChromaVectorStore" in providers_created
        assert "PineconeVectorStore" in providers_created
        assert "QdrantVectorStore" in providers_created
        assert "WeaviateVectorStore" in providers_created

    def test_factory_with_embeddings_integration(self, config_chroma):
        """Test factory works with real embeddings mock."""
        # Create more realistic embeddings mock
        embeddings = Mock()
        embeddings.embed_documents.return_value = [[0.1] * 768 for _ in range(3)]
        embeddings.embed_query.return_value = [0.2] * 768
        embeddings.get_dimension.return_value = 768

        # Mock both PersistentClient (used by ChromaDB) and Path.mkdir (filesystem)
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        with patch("chromadb.PersistentClient", return_value=mock_client):
            with patch("pathlib.Path.mkdir"):
                vectorstore = create_vectorstore(config_chroma, embeddings)

                assert vectorstore is not None
                assert hasattr(vectorstore, "embeddings")
                # Embeddings should work
                query_embedding = embeddings.embed_query("test")
                assert len(query_embedding) == 768
