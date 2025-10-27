"""
Tests for configuration with test.toml.

Tests that configuration is properly loaded from test.toml with dummy values.
All tests run with APP_ENV=test (set in conftest.py).

Test Coverage:
- Test environment is properly set
- Dummy API keys are loaded
- All config sections are populated
- No real credentials needed for testing
"""

import pytest
from config import Config


class TestTestEnvironmentConfig:
    """Test that test.toml is loaded correctly"""
    
    def test_app_environment_is_test(self):
        """Test that APP_ENV is set to 'test'"""
        config = Config()
        assert config.app.environment == "test"
        assert config.AppEnv == "test"
    
    def test_app_name_is_test_variant(self):
        """Test that app name reflects test environment"""
        config = Config()
        assert config.app.name == "ragtrial-app-test"


class TestConfigValues:
    """Test that configuration values are loaded correctly"""
    
    def test_embeddings_provider_set(self):
        """Test embeddings provider is set"""
        config = Config()
        assert config.embeddings.provider == "google"
    
    def test_embeddings_dimension_set(self):
        """Test embeddings dimension is set"""
        config = Config()
        assert config.embeddings.dimension == 768
    
    def test_vectorstore_provider_set(self):
        """Test vectorstore provider is set"""
        config = Config()
        assert config.vectorstore.provider == "chroma"
    
    def test_google_model_set(self):
        """Test Google model is set"""
        config = Config()
        assert config.embeddings.google.model is not None
    
    def test_openai_model_set(self):
        """Test OpenAI model is set"""
        config = Config()
        assert config.embeddings.openai.model is not None
    
    def test_huggingface_model_set(self):
        """Test HuggingFace model is set"""
        config = Config()
        assert config.embeddings.huggingface.model_name is not None


class TestTestEnvironmentOptimizations:
    """Test that test.toml has optimizations for testing"""
    
    def test_logging_level_is_warning(self):
        """Test logging level is WARNING to reduce test noise"""
        config = Config()
        assert config.logging.level == "WARNING"
    
    def test_separate_test_storage_paths(self):
        """Test that test environment uses separate storage"""
        config = Config()
        # Chroma should use test-specific path
        assert "test" in config.vectorstore.chroma.persist_directory.lower()
        # HuggingFace should use test cache
        assert "test" in config.embeddings.huggingface.cache_folder.lower()


class TestAllConfigSectionsPopulated:
    """Test that all configuration sections are properly loaded"""
    
    def test_app_section_populated(self):
        """Test [app] section is populated"""
        config = Config()
        assert hasattr(config, 'app')
        assert config.app.name is not None
        assert config.app.version is not None
        assert config.app.environment is not None
    
    def test_embeddings_section_populated(self):
        """Test [embeddings] section is populated"""
        config = Config()
        assert hasattr(config, 'embeddings')
        assert config.embeddings.provider is not None
        assert config.embeddings.dimension is not None
    
    def test_google_embeddings_populated(self):
        """Test Google embeddings config is populated"""
        config = Config()
        assert hasattr(config.embeddings, 'google')
        assert config.embeddings.google.model is not None
    
    def test_openai_embeddings_populated(self):
        """Test OpenAI embeddings config is populated"""
        config = Config()
        assert hasattr(config.embeddings, 'openai')
        assert config.embeddings.openai.model is not None
        assert config.embeddings.openai.dimensions is not None
    
    def test_huggingface_embeddings_populated(self):
        """Test HuggingFace embeddings config is populated"""
        config = Config()
        assert hasattr(config.embeddings, 'huggingface')
        assert config.embeddings.huggingface.model_name is not None
        assert config.embeddings.huggingface.device is not None
    
    def test_anthropic_embeddings_populated(self):
        """Test Anthropic embeddings config is populated"""
        config = Config()
        assert hasattr(config.embeddings, 'anthropic')
        assert config.embeddings.anthropic.model is not None
    
    def test_vectorstore_section_populated(self):
        """Test [vectorstore] section is populated"""
        config = Config()
        assert hasattr(config, 'vectorstore')
        assert config.vectorstore.provider is not None
    
    def test_chroma_vectorstore_populated(self):
        """Test Chroma config is populated"""
        config = Config()
        assert hasattr(config.vectorstore, 'chroma')
        assert config.vectorstore.chroma.persist_directory is not None
    
    def test_pinecone_vectorstore_populated(self):
        """Test Pinecone config is populated"""
        config = Config()
        assert hasattr(config.vectorstore, 'pinecone')
        assert config.vectorstore.pinecone.index_name is not None
    
    def test_qdrant_vectorstore_populated(self):
        """Test Qdrant config is populated"""
        config = Config()
        assert hasattr(config.vectorstore, 'qdrant')
        # Qdrant config exists
    
    def test_weaviate_vectorstore_populated(self):
        """Test Weaviate config is populated"""
        config = Config()
        assert hasattr(config.vectorstore, 'weaviate')
        assert config.vectorstore.weaviate.class_name is not None
    
    def test_logging_section_populated(self):
        """Test [logging] section is populated"""
        config = Config()
        assert hasattr(config, 'logging')
        assert config.logging.level is not None
        assert config.logging.format is not None


class TestConfigInstances:
    """Test Config instantiation"""
    
    def test_config_values_consistent_across_calls(self):
        """Test that config values are consistent across instances"""
        config1 = Config()
        config2 = Config()
        
        # Values should be consistent even if instances are different
        assert config1.app.name == config2.app.name
        assert config1.app.environment == config2.app.environment
        assert config1.embeddings.provider == config2.embeddings.provider
