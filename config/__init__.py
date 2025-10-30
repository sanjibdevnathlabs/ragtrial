"""
Configuration module for RAG application.

This module provides a singleton Config class that loads settings from TOML files
and makes them available throughout the application.

Configuration classes are organized by domain in separate modules:
- app: Application metadata configuration
- logging: Logging configuration
- api: API server configuration
- storage: Storage backend configuration
- database: Database configuration (SQLite, MySQL, PostgreSQL)
- vectorstore: Vector store configuration (Chroma, Pinecone, Qdrant, Weaviate)
- embeddings: Embeddings provider configuration
- llm: LLM provider configuration
- rag: RAG chain configuration
"""

import os
import tomllib  # Built-in TOML parser for Python 3.11+
from pathlib import Path

# Import trace codes
from trace import codes

from config.api import APIConfig
from config.ui import UIConfig

# Import configuration classes needed internally by Config class
from config.app import AppConfig
from config.database import (
    DatabaseConfig,
    MySQLConfig,
    MySQLReadConfig,
    MySQLWriteConfig,
    PostgreSQLConfig,
    PostgreSQLReadConfig,
    PostgreSQLWriteConfig,
    SQLiteConfig,
    SQLiteReadConfig,
    SQLiteWriteConfig,
)
from config.embeddings import (
    AnthropicEmbeddingsConfig,
    EmbeddingsConfig,
    GoogleEmbeddingsConfig,
    HuggingFaceEmbeddingsConfig,
    OpenAIEmbeddingsConfig,
)
from config.llm import AnthropicLLMConfig, GoogleLLMConfig, OpenAILLMConfig
from config.logging import LoggingConfig
from config.rag import GoogleConfig, RAGConfig
from config.storage import LocalStorageConfig, S3StorageConfig, StorageConfig
from config.vectorstore import (
    ChromaConfig,
    PineconeConfig,
    QdrantConfig,
    VectorStoreConfig,
    WeaviateConfig,
)

# Import logger for early logging (before setup_logging is called)
from logger import get_logger

# Import singleton metaclass for thread-safe singleton pattern
from utils.singleton import SingletonMeta

# Initialize logger for config module
logger = get_logger(__name__)


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

    # UI configuration
    ui: UIConfig

    # Vector store configuration
    vectorstore: VectorStoreConfig

    # Embeddings configuration
    embeddings: EmbeddingsConfig

    # RAG configuration
    rag: RAGConfig

    # Database configuration
    database: DatabaseConfig

    # This will hold the name of the loaded environment, e.g., "prod"
    AppEnv: str = None

    def __init__(self):
        """
        Initialize configuration from TOML files.

        Due to singleton pattern, this only runs once per process.
        """
        # Singleton guard: only initialize once
        if hasattr(self, "_initialized"):
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
        self.ui = UIConfig()

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

        self.database = DatabaseConfig()
        self.database.sqlite = SQLiteConfig()
        self.database.sqlite.write = SQLiteWriteConfig()
        self.database.sqlite.read = SQLiteReadConfig()
        self.database.mysql = MySQLConfig()
        self.database.mysql.write = MySQLWriteConfig()
        self.database.mysql.read = MySQLReadConfig()
        self.database.postgresql = PostgreSQLConfig()
        self.database.postgresql.write = PostgreSQLWriteConfig()
        self.database.postgresql.read = PostgreSQLReadConfig()

    def _load_config_files(self) -> dict:
        """Load and merge TOML configuration files."""
        config_dir = Path(__file__).parent.parent / "environment"
        default_config_path = config_dir / "default.toml"

        settings = self._load_toml(default_config_path)

        # Default to 'dev' environment if APP_ENV is not set
        if "APP_ENV" not in os.environ:
            os.environ["APP_ENV"] = "dev"

        self.AppEnv = os.environ["APP_ENV"]

        env_config_path = config_dir / f"{self.AppEnv}.toml"
        if not env_config_path.exists():
            logger.warning(
                codes.CONFIG_LOADING,
                message=(
                    f"APP_ENV set to '{self.AppEnv}' but "
                    f"{env_config_path.name} not found"
                ),
            )
            return self._interpolate(settings)

        logger.info(
            codes.CONFIG_LOADING,
            message=codes.MSG_LOADING_OVERRIDE_CONFIG,
            file=env_config_path.name,
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
        self._populate_config_section(
            vectorstore_settings, "chroma", self.vectorstore.chroma
        )
        self._populate_config_section(
            vectorstore_settings, "pinecone", self.vectorstore.pinecone
        )
        self._populate_config_section(
            vectorstore_settings, "qdrant", self.vectorstore.qdrant
        )
        self._populate_config_section(
            vectorstore_settings, "weaviate", self.vectorstore.weaviate
        )

        embeddings_settings = settings.get("embeddings", {})
        self._populate_config_section(
            embeddings_settings, "google", self.embeddings.google
        )
        self._populate_config_section(
            embeddings_settings, "openai", self.embeddings.openai
        )
        self._populate_config_section(
            embeddings_settings, "huggingface", self.embeddings.huggingface
        )
        self._populate_config_section(
            embeddings_settings, "anthropic", self.embeddings.anthropic
        )

        # Populate RAG configuration
        self._populate_config_section(settings, "rag", self.rag)

        rag_settings = settings.get("rag", {})
        self._populate_config_section(rag_settings, "google", self.rag.google)
        self._populate_config_section(rag_settings, "openai", self.rag.openai)
        self._populate_config_section(rag_settings, "anthropic", self.rag.anthropic)

        # Populate database configuration
        self._populate_config_section(settings, "database", self.database)

        database_settings = settings.get("database", {})

        # Populate SQLite configuration
        sqlite_settings = database_settings.get("sqlite", {})
        self._populate_config_section(
            sqlite_settings, "write", self.database.sqlite.write
        )
        self._populate_config_section(
            sqlite_settings, "read", self.database.sqlite.read
        )

        # Populate MySQL configuration
        mysql_settings = database_settings.get("mysql", {})
        self._populate_config_section(
            mysql_settings, "write", self.database.mysql.write
        )
        self._populate_config_section(mysql_settings, "read", self.database.mysql.read)

        # Populate PostgreSQL configuration
        postgresql_settings = database_settings.get("postgresql", {})
        self._populate_config_section(
            postgresql_settings, "write", self.database.postgresql.write
        )
        self._populate_config_section(
            postgresql_settings, "read", self.database.postgresql.read
        )

        logger.info(codes.CONFIG_LOADED, message=codes.MSG_CONFIG_LOADED)

    def _validate_config(self) -> None:
        """
        Validate configuration values and log warnings for missing required
        fields.
        """
        if not self.google.api_key:
            logger.warning(
                codes.VALIDATION_ERROR, message=codes.MSG_GOOGLE_API_KEY_MISSING
            )

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
        self, settings: dict, section_name: str, config_obj
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
