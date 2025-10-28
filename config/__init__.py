
import os
import tomllib  # Built-in TOML parser for Python 3.11+
from pathlib import Path

# Import trace codes
from trace import codes

# Import logger for early logging (before setup_logging is called)
from logger import get_logger

# Import singleton metaclass for thread-safe singleton pattern
from utils.singleton import SingletonMeta

# Initialize logger for config module
logger = get_logger(__name__)



class AppConfig:
    """Holds application metadata from the [app] TOML section"""
    name: str = None
    environment: str = None
    version: str = None


class LoggingConfig:
    """Holds logging configuration from the [logging] TOML section"""
    level: str = "INFO"
    format: str = "console"
    include_caller: bool = False
    include_process_info: bool = False


class GoogleConfig:
    """Holds settings from the [google] TOML section"""
    api_key: str = None


# ============================================================================
# STORAGE BACKEND CONFIGS
# ============================================================================

class LocalStorageConfig:
    """Local storage-specific configuration"""
    path: str = "source_docs"
    create_if_missing: bool = True


class S3StorageConfig:
    """S3 storage-specific configuration"""
    bucket_name: str = "rag-documents"
    region: str = "us-east-1"
    use_explicit_credentials: bool = False
    access_key_id: str = ""
    secret_access_key: str = ""
    endpoint_url: str = ""
    use_localstack: bool = False
    role_arn: str = ""
    role_session_name: str = "rag-app"


class StorageConfig:
    """Storage backend configuration"""
    backend: str = "local"
    max_file_size_mb: int = 100
    allowed_extensions: list = None
    local: LocalStorageConfig = None
    s3: S3StorageConfig = None


# ============================================================================
# API CONFIGS
# ============================================================================

class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = None
    upload_chunk_size: int = 1048576  # 1MB


# ============================================================================
# VECTORSTORE PROVIDER CONFIGS
# ============================================================================

class ChromaConfig:
    """ChromaDB-specific configuration"""
    persist_directory: str = "storage/chroma"
    distance_function: str = "cosine"
    anonymized_telemetry: bool = False


class PineconeConfig:
    """Pinecone-specific configuration"""
    api_key: str = None
    cloud: str = "aws"           # Cloud provider: aws, gcp, azure
    region: str = "us-east-1"    # Cloud region (AWS: us-east-1, GCP: us-central1, Azure: eastus)
    index_name: str = "rag-documents"
    dimension: int = 768
    metric: str = "cosine"       # Similarity metric: cosine, euclidean, dotproduct
    verify_ssl: bool = True      # SSL certificate verification (disable for dev if needed)


class QdrantConfig:
    """Qdrant-specific configuration"""
    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    prefer_grpc: bool = False
    api_key: str = ""
    distance: str = "Cosine"


class WeaviateConfig:
    """Weaviate-specific configuration"""
    url: str = "http://localhost:8080"
    api_key: str = ""
    class_name: str = "RagDocument"
    distance: str = "cosine"
    grpc_port: int = 50051  # Default gRPC port (must differ from HTTP port)
    default_http_port: int = 8080  # Default HTTP port if not in URL
    default_https_port: int = 443  # Default HTTPS port if not in URL


class VectorStoreConfig:
    """Vector store configuration"""
    provider: str = "chroma"
    collection_name: str = "rag_documents"
    chroma: ChromaConfig = None
    pinecone: PineconeConfig = None
    qdrant: QdrantConfig = None
    weaviate: WeaviateConfig = None


# ============================================================================
# EMBEDDINGS PROVIDER CONFIGS
# ============================================================================

class GoogleEmbeddingsConfig:
    """Google embeddings-specific configuration"""
    model: str = "models/text-embedding-004"
    task_type: str = "retrieval_document"
    batch_size: int = 100
    title: str = ""


class OpenAIEmbeddingsConfig:
    """OpenAI embeddings-specific configuration"""
    api_key: str = None
    model: str = "text-embedding-3-small"
    batch_size: int = 100
    dimensions: int = 1536
    verify_ssl: bool = True


class HuggingFaceEmbeddingsConfig:
    """HuggingFace embeddings-specific configuration"""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    cache_folder: str = "models/huggingface"
    device: str = "cpu"


class AnthropicEmbeddingsConfig:
    """Anthropic (Voyage AI) embeddings-specific configuration"""
    api_key: str = None
    model: str = "voyage-2"
    input_type: str = "document"
    batch_size: int = 128
    verify_ssl: bool = True


class EmbeddingsConfig:
    """Embeddings configuration"""
    provider: str = "google"
    dimension: int = 768
    google: GoogleEmbeddingsConfig = None
    openai: OpenAIEmbeddingsConfig = None
    huggingface: HuggingFaceEmbeddingsConfig = None
    anthropic: AnthropicEmbeddingsConfig = None


# ============================================================================
# LLM (LARGE LANGUAGE MODEL) PROVIDER CONFIGS
# ============================================================================

class GoogleLLMConfig:
    """Google (Gemini) LLM-specific configuration"""
    api_key: str = None
    model: str = "gemini-2.0-flash"
    temperature: float = 0.1
    max_tokens: int = 1000


class OpenAILLMConfig:
    """OpenAI (GPT) LLM-specific configuration"""
    api_key: str = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 1000
    verify_ssl: bool = True


class AnthropicLLMConfig:
    """Anthropic (Claude) LLM-specific configuration"""
    api_key: str = None
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.1
    max_tokens: int = 1000
    verify_ssl: bool = True


# ============================================================================
# RAG (RETRIEVAL-AUGMENTED GENERATION) CONFIG
# ============================================================================

class RAGConfig:
    """RAG (Retrieval-Augmented Generation) configuration"""
    provider: str = "google"
    retrieval_k: int = 5
    google: GoogleLLMConfig = None
    openai: OpenAILLMConfig = None
    anthropic: AnthropicLLMConfig = None


class Config(metaclass=SingletonMeta):
    """
    The main config object, populated from TOML files.
    Attributes are pre-defined here for safety and clarity.
    
    This class is a singleton - only one instance exists per process,
    ensuring consistent configuration across the application.
    """
    
    # Application metadata
    app: AppConfig
    
    # Logging configuration
    logging: LoggingConfig
    
    # This attribute will hold all settings from the [google] section
    google: GoogleConfig
    
    # Storage backend configuration
    storage: StorageConfig
    
    # API configuration
    api: APIConfig
    
    # Vector store configuration
    vectorstore: VectorStoreConfig
    
    # Embeddings configuration
    embeddings: EmbeddingsConfig
    
    # RAG configuration
    rag: RAGConfig
    
    # This will hold the name of the loaded environment, e.g., "prod"
    AppEnv: str = None

    def __init__(self):
        """
        Initialize configuration from TOML files.
        
        Due to singleton pattern, this only runs once per process.
        """
        # Singleton guard: only initialize once
        if hasattr(self, '_initialized'):
            return
        
        self._initialize_config_objects()
        settings = self._load_config_files()
        self._apply_config_values(settings)
        self._validate_config()
        
        # Mark as initialized
        self._initialized = True

    def _initialize_config_objects(self) -> None:
        """Initialize all configuration objects with default values."""
        self.app = AppConfig()
        self.logging = LoggingConfig()
        self.google = GoogleConfig()
        
        self.storage = StorageConfig()
        self.storage.local = LocalStorageConfig()
        self.storage.s3 = S3StorageConfig()
        
        self.api = APIConfig()
        
        self.vectorstore = VectorStoreConfig()
        self.vectorstore.chroma = ChromaConfig()
        self.vectorstore.pinecone = PineconeConfig()
        self.vectorstore.qdrant = QdrantConfig()
        self.vectorstore.weaviate = WeaviateConfig()
        
        self.embeddings = EmbeddingsConfig()
        self.embeddings.google = GoogleEmbeddingsConfig()
        self.embeddings.openai = OpenAIEmbeddingsConfig()
        self.embeddings.huggingface = HuggingFaceEmbeddingsConfig()
        self.embeddings.anthropic = AnthropicEmbeddingsConfig()
        
        self.rag = RAGConfig()
        self.rag.google = GoogleLLMConfig()
        self.rag.openai = OpenAILLMConfig()
        self.rag.anthropic = AnthropicLLMConfig()

    def _load_config_files(self) -> dict:
        """Load and merge TOML configuration files."""
        config_dir = Path(__file__).parent.parent / "environment"
        default_config_path = config_dir / "default.toml"
        
        settings = self._load_toml(default_config_path)
        
        self.AppEnv = os.environ.get("APP_ENV")
        if not self.AppEnv:
            return self._interpolate(settings)
        
        env_config_path = config_dir / f"{self.AppEnv}.toml"
        if not env_config_path.exists():
            logger.warning(
                codes.CONFIG_LOADING,
                message=f"APP_ENV set to '{self.AppEnv}' but {env_config_path.name} not found"
            )
            return self._interpolate(settings)
        
        logger.info(
            codes.CONFIG_LOADING,
            message=codes.MSG_LOADING_OVERRIDE_CONFIG,
            file=env_config_path.name
        )
        env_config = self._load_toml(env_config_path)
        self._merge_dicts(settings, env_config)
        
        return self._interpolate(settings)

    def _apply_config_values(self, settings: dict) -> None:
        """Apply loaded settings to configuration objects."""
        self._populate_config_section(settings, "app", self.app)
        self._populate_config_section(settings, "logging", self.logging)
        self._populate_config_section(settings, "google", self.google)
        self._populate_config_section(settings, "storage", self.storage)
        self._populate_config_section(settings, "api", self.api)
        self._populate_config_section(settings, "vectorstore", self.vectorstore)
        self._populate_config_section(settings, "embeddings", self.embeddings)
        
        storage_settings = settings.get("storage", {})
        self._populate_config_section(storage_settings, "local", self.storage.local)
        self._populate_config_section(storage_settings, "s3", self.storage.s3)
        
        vectorstore_settings = settings.get("vectorstore", {})
        self._populate_config_section(vectorstore_settings, "chroma", self.vectorstore.chroma)
        self._populate_config_section(vectorstore_settings, "pinecone", self.vectorstore.pinecone)
        self._populate_config_section(vectorstore_settings, "qdrant", self.vectorstore.qdrant)
        self._populate_config_section(vectorstore_settings, "weaviate", self.vectorstore.weaviate)
        
        embeddings_settings = settings.get("embeddings", {})
        self._populate_config_section(embeddings_settings, "google", self.embeddings.google)
        self._populate_config_section(embeddings_settings, "openai", self.embeddings.openai)
        self._populate_config_section(embeddings_settings, "huggingface", self.embeddings.huggingface)
        self._populate_config_section(embeddings_settings, "anthropic", self.embeddings.anthropic)
        
        # Populate RAG configuration
        self._populate_config_section(settings, "rag", self.rag)
        
        rag_settings = settings.get("rag", {})
        self._populate_config_section(rag_settings, "google", self.rag.google)
        self._populate_config_section(rag_settings, "openai", self.rag.openai)
        self._populate_config_section(rag_settings, "anthropic", self.rag.anthropic)
        
        logger.info(codes.CONFIG_LOADED, message=codes.MSG_CONFIG_LOADED)

    def _validate_config(self) -> None:
        """Validate configuration values and log warnings for missing required fields."""
        if not self.google.api_key:
            logger.warning(codes.VALIDATION_ERROR, message=codes.MSG_GOOGLE_API_KEY_MISSING)
        
        if not self.app.name:
            logger.warning(codes.VALIDATION_ERROR, message=codes.MSG_APP_NAME_MISSING)

    def _load_toml(self, file_path: Path) -> dict:
        """Loads a single TOML file."""
        if not file_path.exists():
            raise FileNotFoundError(f"{codes.MSG_CONFIG_FILE_NOT_FOUND}: {file_path}")
        
        with open(file_path, "rb") as f:
            return tomllib.load(f)

    def _merge_dicts(self, base: dict, override: dict):
        """Recursively merges the 'override' dict into the 'base' dict."""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._merge_dicts(base[key], value)
                continue
            
            base[key] = value

    def _interpolate(self, item):
        """Recursively replaces $VAR or ${VAR} in any string value."""
        if isinstance(item, dict):
            for key, value in item.items():
                item[key] = self._interpolate(value)
            return item
        
        if isinstance(item, list):
            for i, value in enumerate(item):
                item[i] = self._interpolate(value)
            return item
        
        if isinstance(item, str):
            return os.path.expandvars(item)
        
        return item

    def _populate_config_section(
        self,
        settings: dict,
        section_name: str,
        config_obj
    ) -> None:
        """
        Dynamically populate a config object from settings dictionary.
        
        This method automatically detects all attributes in the config object
        and sets them if they exist in the TOML settings. No manual field list needed!
        
        Args:
            settings: The loaded settings dictionary from TOML files
            section_name: Name of the TOML section (e.g., "app", "logging", "google")
            config_obj: The config object to populate (e.g., self.app, self.logging)
            
        Example:
            self._populate_config_section(settings, "app", self.app)
            # Automatically sets all fields found in [app] section
        
        Benefits:
            - Zero maintenance: Add new field to config class, it works automatically
            - Type-safe: Only sets fields that exist in the config class
            - TOML-driven: Settings file determines what gets populated
        """
        section_settings = settings.get(section_name, {})
        
        # If section_settings is a dict, populate the config object's attributes
        if isinstance(section_settings, dict):
            for field, value in section_settings.items():
                # Skip nested dicts - they're sub-sections, not values
                # (e.g., [vectorstore.chroma] is handled separately)
                if isinstance(value, dict):
                    continue
                    
                # Only set if the config object has this attribute (type-safe)
                if hasattr(config_obj, field):
                    setattr(config_obj, field, value)
