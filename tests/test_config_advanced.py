"""
Comprehensive tests for advanced config features:
1. Environment variable interpolation ($VAR and ${VAR})
2. TOML override mechanism (dev.toml overrides default.toml)
3. All config fields properly populated
"""

import os
import pytest
from config import Config


class TestEnvironmentVariableInterpolation:
    """Test that environment variables are interpolated in config values"""
    
    def test_gemini_api_key_interpolation(self):
        """Test that GEMINI_API_KEY is interpolated from environment"""
        # Ensure env var is set (should be in ~/.zshrc)
        gemini_key = os.environ.get("GEMINI_API_KEY")
        
        if not gemini_key:
            pytest.skip("GEMINI_API_KEY not set in environment")
        
        config = Config()
        
        # Config should have the actual env var value, not the placeholder
        assert config.google.api_key == gemini_key
        assert config.google.api_key != "$GEMINI_API_KEY"
        assert config.google.api_key != "${GEMINI_API_KEY}"
    
    def test_pinecone_api_key_interpolation(self):
        """Test that PINECONE_API_KEY is interpolated from environment"""
        pinecone_key = os.environ.get("PINECONE_API_KEY")
        
        if not pinecone_key:
            pytest.skip("PINECONE_API_KEY not set in environment")
        
        config = Config()
        
        # Config should have the actual env var value
        assert config.vectorstore.pinecone.api_key == pinecone_key
        assert config.vectorstore.pinecone.api_key != "$PINECONE_API_KEY"
    
    def test_qdrant_api_key_interpolation(self):
        """Test that QDRANT_API_KEY is interpolated from environment"""
        qdrant_key = os.environ.get("QDRANT_API_KEY")
        
        if not qdrant_key:
            pytest.skip("QDRANT_API_KEY not set in environment")
        
        config = Config()
        
        # Config should have the actual env var value
        assert config.vectorstore.qdrant.api_key == qdrant_key
        assert config.vectorstore.qdrant.api_key != "$QDRANT_API_KEY"
    
    def test_weaviate_api_key_interpolation(self):
        """Test that WEAVIATE_API_KEY is interpolated from environment"""
        weaviate_key = os.environ.get("WEAVIATE_API_KEY")
        
        if not weaviate_key:
            pytest.skip("WEAVIATE_API_KEY not set in environment")
        
        config = Config()
        
        # Config should have the actual env var value
        assert config.vectorstore.weaviate.api_key == weaviate_key
        assert config.vectorstore.weaviate.api_key != "$WEAVIATE_API_KEY"
    
    def test_app_env_interpolation(self):
        """Test that APP_ENV is interpolated from environment"""
        app_env = os.environ.get("APP_ENV", "NOT_SET")
        
        config = Config()
        
        # Config should have the actual env var value
        # Note: APP_ENV might be empty string if not set
        if app_env != "NOT_SET":
            assert config.app.environment == app_env
            assert config.app.environment != "$APP_ENV"


class TestTOMLOverrideMechanism:
    """Test that environment-specific TOML files override default.toml"""
    
    def test_dev_toml_overrides_applied(self):
        """Test that dev.toml values override default.toml when APP_ENV=dev"""
        app_env = os.environ.get("APP_ENV")
        
        if app_env != "dev":
            pytest.skip("APP_ENV is not set to 'dev', skipping override test")
        
        config = Config()
        
        # dev.toml sets verify_ssl to false (overriding default.toml's true)
        assert config.vectorstore.pinecone.verify_ssl == False, \
            "Pinecone verify_ssl should be False from dev.toml override"
    
    def test_non_overridden_values_from_default(self):
        """Test that non-overridden values still come from default.toml"""
        config = Config()
        
        # These values should be from default.toml (not overridden in dev.toml)
        assert config.vectorstore.pinecone.cloud == "aws"
        assert config.vectorstore.pinecone.region == "us-east-1"
        assert config.vectorstore.pinecone.metric == "cosine"
    
    def test_app_env_tracking(self):
        """Test that Config tracks which environment was loaded"""
        app_env = os.environ.get("APP_ENV")
        
        config = Config()
        
        # Config should track the APP_ENV value
        assert config.AppEnv == app_env


class TestConfigFieldsPopulated:
    """Test that all config fields are properly populated from TOML"""
    
    def test_pinecone_all_fields_populated(self):
        """Test that ALL Pinecone fields are populated from TOML"""
        config = Config()
        
        # Check all Pinecone fields exist and are populated
        assert hasattr(config.vectorstore.pinecone, 'api_key')
        assert hasattr(config.vectorstore.pinecone, 'cloud')
        assert hasattr(config.vectorstore.pinecone, 'region')
        assert hasattr(config.vectorstore.pinecone, 'index_name')
        assert hasattr(config.vectorstore.pinecone, 'dimension')
        assert hasattr(config.vectorstore.pinecone, 'metric')
        assert hasattr(config.vectorstore.pinecone, 'verify_ssl')
        
        # Check values are correct (from TOML, not class defaults)
        assert config.vectorstore.pinecone.cloud == "aws"
        assert config.vectorstore.pinecone.region == "us-east-1"
        assert config.vectorstore.pinecone.index_name == "rag-documents"
        assert config.vectorstore.pinecone.dimension == 768
        assert config.vectorstore.pinecone.metric == "cosine"
        
        # verify_ssl depends on APP_ENV
        app_env = os.environ.get("APP_ENV")
        if app_env == "dev":
            assert config.vectorstore.pinecone.verify_ssl == False
        else:
            assert config.vectorstore.pinecone.verify_ssl == True
    
    def test_weaviate_all_fields_populated(self):
        """Test that ALL Weaviate fields are populated from TOML"""
        config = Config()
        
        # Check all Weaviate fields exist and are populated
        assert hasattr(config.vectorstore.weaviate, 'url')
        assert hasattr(config.vectorstore.weaviate, 'api_key')
        assert hasattr(config.vectorstore.weaviate, 'class_name')
        assert hasattr(config.vectorstore.weaviate, 'distance')
        assert hasattr(config.vectorstore.weaviate, 'grpc_port')
        assert hasattr(config.vectorstore.weaviate, 'default_http_port')
        assert hasattr(config.vectorstore.weaviate, 'default_https_port')
        
        # Check values are correct (from TOML)
        assert config.vectorstore.weaviate.url == "http://localhost:8080"
        assert config.vectorstore.weaviate.class_name == "RagDocument"
        assert config.vectorstore.weaviate.distance == "cosine"
        assert config.vectorstore.weaviate.grpc_port == 50051
        assert config.vectorstore.weaviate.default_http_port == 8080
        assert config.vectorstore.weaviate.default_https_port == 443
    
    def test_qdrant_all_fields_populated(self):
        """Test that ALL Qdrant fields are populated from TOML"""
        config = Config()
        
        # Check all Qdrant fields exist
        assert hasattr(config.vectorstore.qdrant, 'host')
        assert hasattr(config.vectorstore.qdrant, 'port')
        assert hasattr(config.vectorstore.qdrant, 'grpc_port')
        assert hasattr(config.vectorstore.qdrant, 'prefer_grpc')
        assert hasattr(config.vectorstore.qdrant, 'api_key')
        assert hasattr(config.vectorstore.qdrant, 'distance')
        
        # Check values from TOML
        assert config.vectorstore.qdrant.host == "localhost"
        assert config.vectorstore.qdrant.port == 6333
        assert config.vectorstore.qdrant.grpc_port == 6334
        assert config.vectorstore.qdrant.prefer_grpc == False
        assert config.vectorstore.qdrant.distance == "Cosine"
    
    def test_chroma_all_fields_populated(self):
        """Test that ALL ChromaDB fields are populated from TOML"""
        config = Config()
        
        # Check all ChromaDB fields exist
        assert hasattr(config.vectorstore.chroma, 'persist_directory')
        assert hasattr(config.vectorstore.chroma, 'distance_function')
        assert hasattr(config.vectorstore.chroma, 'anonymized_telemetry')
        
        # Check values from TOML
        assert config.vectorstore.chroma.persist_directory == "storage/chroma"
        assert config.vectorstore.chroma.distance_function == "cosine"
        assert config.vectorstore.chroma.anonymized_telemetry == False


class TestEmbeddingsConfig:
    """Test embeddings configuration"""
    
    def test_embeddings_provider_config(self):
        """Test that embeddings provider config is loaded"""
        config = Config()
        
        # Check top-level embeddings config
        assert config.embeddings.provider == "google"
        assert config.embeddings.dimension == 768
    
    def test_google_embeddings_config(self):
        """Test Google embeddings config"""
        config = Config()
        
        assert config.embeddings.google.model == "models/text-embedding-004"
        assert config.embeddings.google.task_type == "retrieval_document"
        assert config.embeddings.google.batch_size == 100
    
    def test_openai_embeddings_config(self):
        """Test OpenAI embeddings config"""
        config = Config()
        
        assert config.embeddings.openai.model == "text-embedding-3-small"
        assert config.embeddings.openai.batch_size == 100
        assert config.embeddings.openai.dimensions == 1536
    
    def test_huggingface_embeddings_config(self):
        """Test HuggingFace embeddings config"""
        config = Config()
        
        assert config.embeddings.huggingface.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.embeddings.huggingface.cache_folder == "models/huggingface"
        assert config.embeddings.huggingface.device == "cpu"
    
    def test_anthropic_embeddings_config(self):
        """Test Anthropic (Voyage AI) embeddings config"""
        config = Config()
        
        assert config.embeddings.anthropic.model == "voyage-2"
        assert config.embeddings.anthropic.input_type == "document"
        assert config.embeddings.anthropic.batch_size == 128


class TestConfigIntegrity:
    """Test overall config system integrity"""
    
    def test_config_instantiation_no_errors(self):
        """Test that Config can be instantiated without errors"""
        try:
            config = Config()
            assert config is not None
        except Exception as e:
            pytest.fail(f"Config instantiation raised exception: {e}")
    
    def test_all_required_sections_present(self):
        """Test that all required config sections are present"""
        config = Config()
        
        # Check all major sections exist
        assert hasattr(config, 'app')
        assert hasattr(config, 'logging')
        assert hasattr(config, 'google')
        assert hasattr(config, 'vectorstore')
        assert hasattr(config, 'embeddings')
        
        # Check vectorstore providers exist
        assert hasattr(config.vectorstore, 'chroma')
        assert hasattr(config.vectorstore, 'pinecone')
        assert hasattr(config.vectorstore, 'qdrant')
        assert hasattr(config.vectorstore, 'weaviate')
        
        # Check embeddings providers exist
        assert hasattr(config.embeddings, 'google')
        assert hasattr(config.embeddings, 'openai')
        assert hasattr(config.embeddings, 'huggingface')
        assert hasattr(config.embeddings, 'anthropic')
    
    def test_config_values_not_none_where_expected(self):
        """Test that critical config values are not None"""
        config = Config()
        
        # App config should have values
        assert config.app.name is not None
        assert config.app.version is not None
        
        # Logging config should have values
        assert config.logging.level is not None
        assert config.logging.format is not None
        
        # Vectorstore should have provider
        assert config.vectorstore.provider is not None
        assert config.vectorstore.collection_name is not None
        
        # Embeddings should have provider
        assert config.embeddings.provider is not None
        assert config.embeddings.dimension is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
