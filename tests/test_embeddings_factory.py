"""
Tests for embeddings factory.

Unit tests with FULL MOCKING - no actual provider instantiation.
Following industry best practices:
- No model downloads
- No API calls
- No network access
- Fast, isolated tests suitable for CI/CD

Test Coverage:
- Factory provider creation for all supported providers (MOCKED)
- Error handling for invalid providers
- Configuration loading and validation
- Provider type verification
"""

from unittest.mock import MagicMock, patch

import pytest

from config import Config
from embeddings import create_embeddings

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def config_google():
    """Get singleton config and set Google provider."""
    config = Config()
    config.embeddings.provider = "google"
    return config


@pytest.fixture
def config_openai():
    """Get singleton config and set OpenAI provider."""
    config = Config()
    config.embeddings.provider = "openai"
    return config


@pytest.fixture
def config_huggingface():
    """Get singleton config and set HuggingFace provider."""
    config = Config()
    config.embeddings.provider = "huggingface"
    return config


@pytest.fixture
def config_anthropic():
    """Get singleton config and set Anthropic provider."""
    config = Config()
    config.embeddings.provider = "anthropic"
    return config


@pytest.fixture
def config_invalid():
    """Create config with invalid provider (using test.toml)."""
    config = Config()
    config.embeddings.provider = "invalid_provider"
    return config


# ============================================================================
# FACTORY TESTS - Provider Creation (MOCKED)
# ============================================================================


class TestEmbeddingsFactory:
    """Test embeddings factory creation with mocked providers."""

    def test_create_google_embeddings(self, config_google):
        """Test creating Google embeddings provider (MOCKED)."""
        with patch("google.generativeai.configure"):
            embeddings = create_embeddings(config_google)

            assert embeddings is not None
            # Protocol duck typing - check for required methods
            assert hasattr(embeddings, "embed_documents")
            assert hasattr(embeddings, "embed_query")
            assert hasattr(embeddings, "get_dimension")
            assert callable(embeddings.embed_documents)
            assert callable(embeddings.embed_query)
            assert callable(embeddings.get_dimension)

    def test_create_openai_embeddings(self, config_openai):
        """Test creating OpenAI embeddings provider (MOCKED)."""
        with patch("openai.OpenAI"):
            embeddings = create_embeddings(config_openai)

            assert embeddings is not None
            # Protocol duck typing - check for required methods
            assert hasattr(embeddings, "embed_documents")
            assert hasattr(embeddings, "embed_query")
            assert hasattr(embeddings, "get_dimension")
            assert callable(embeddings.embed_documents)
            assert callable(embeddings.embed_query)
            assert callable(embeddings.get_dimension)

    def test_create_huggingface_embeddings(self, config_huggingface):
        """Test creating HuggingFace embeddings provider (MOCKED - no model download)."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            # Mock the model to avoid downloading
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            embeddings = create_embeddings(config_huggingface)

            assert embeddings is not None
            # Protocol duck typing - check for required methods
            assert hasattr(embeddings, "embed_documents")
            assert hasattr(embeddings, "embed_query")
            assert hasattr(embeddings, "get_dimension")
            assert callable(embeddings.embed_documents)
            assert callable(embeddings.embed_query)
            assert callable(embeddings.get_dimension)

            # Verify model was NOT actually downloaded
            mock_st.assert_called_once()

    def test_create_anthropic_embeddings(self, config_anthropic):
        """Test creating Anthropic embeddings provider (MOCKED)."""
        with patch("voyageai.Client"):
            embeddings = create_embeddings(config_anthropic)

            assert embeddings is not None
            # Protocol duck typing - check for required methods
            assert hasattr(embeddings, "embed_documents")
            assert hasattr(embeddings, "embed_query")
            assert hasattr(embeddings, "get_dimension")
            assert callable(embeddings.embed_documents)
            assert callable(embeddings.embed_query)
            assert callable(embeddings.get_dimension)


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling in factory."""

    def test_invalid_provider_raises_error(self, config_invalid):
        """Test factory raises error for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            create_embeddings(config_invalid)

        assert "Unknown embeddings provider" in str(exc_info.value)
        assert "invalid_provider" in str(exc_info.value)

    def test_factory_validates_provider_name(self, config_invalid):
        """Test factory validates provider names."""
        with pytest.raises(ValueError):
            create_embeddings(config_invalid)


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================


class TestConfiguration:
    """Test configuration handling in factory."""

    def test_factory_uses_config_provider(self, config_google):
        """Test factory uses provider from config."""
        with patch("google.generativeai.configure"):
            embeddings = create_embeddings(config_google)
            assert embeddings is not None

    def test_factory_respects_provider_switching(self, config_google):
        """Test factory respects provider changes."""
        # First provider
        with patch("google.generativeai.configure"):
            embeddings1 = create_embeddings(config_google)
            assert embeddings1 is not None

        # Switch provider
        config_google.embeddings.provider = "openai"
        with patch("openai.OpenAI"):
            embeddings2 = create_embeddings(config_google)
            assert embeddings2 is not None

        # Different provider instances
        assert type(embeddings1).__name__ != type(embeddings2).__name__


# ============================================================================
# PROVIDER VERIFICATION TESTS
# ============================================================================


class TestProviderTypes:
    """Test correct provider types are returned."""

    def test_google_provider_type(self, config_google):
        """Test Google provider returns correct type."""
        with patch("google.generativeai.configure"):
            embeddings = create_embeddings(config_google)
            assert type(embeddings).__name__ == "GoogleEmbeddings"

    def test_openai_provider_type(self, config_openai):
        """Test OpenAI provider returns correct type."""
        with patch("openai.OpenAI"):
            embeddings = create_embeddings(config_openai)
            assert type(embeddings).__name__ == "OpenAIEmbeddings"

    def test_huggingface_provider_type(self, config_huggingface):
        """Test HuggingFace provider returns correct type."""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            embeddings = create_embeddings(config_huggingface)
            assert type(embeddings).__name__ == "HuggingFaceEmbeddings"

    def test_anthropic_provider_type(self, config_anthropic):
        """Test Anthropic provider returns correct type."""
        with patch("voyageai.Client"):
            embeddings = create_embeddings(config_anthropic)
            assert type(embeddings).__name__ == "AnthropicEmbeddings"


# ============================================================================
# INTEGRATION-LIKE TESTS (Still Mocked)
# ============================================================================


class TestFactoryIntegration:
    """Test factory in realistic scenarios (still mocked)."""

    def test_factory_with_all_providers_sequentially(self):
        """Test factory can create all providers in sequence by switching providers."""
        config = Config()
        providers_created = []

        # Google
        config.embeddings.provider = "google"
        with patch("google.generativeai.configure"):
            google_emb = create_embeddings(config)
            providers_created.append(type(google_emb).__name__)

        # OpenAI
        config.embeddings.provider = "openai"
        with patch("openai.OpenAI"):
            openai_emb = create_embeddings(config)
            providers_created.append(type(openai_emb).__name__)

        # HuggingFace
        config.embeddings.provider = "huggingface"
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model
            hf_emb = create_embeddings(config)
            providers_created.append(type(hf_emb).__name__)

        # Anthropic
        config.embeddings.provider = "anthropic"
        with patch("voyageai.Client"):
            anthropic_emb = create_embeddings(config)
            providers_created.append(type(anthropic_emb).__name__)

        # Verify all 4 providers were created
        assert len(providers_created) == 4
        assert "GoogleEmbeddings" in providers_created
        assert "OpenAIEmbeddings" in providers_created
        assert "HuggingFaceEmbeddings" in providers_created
        assert "AnthropicEmbeddings" in providers_created
