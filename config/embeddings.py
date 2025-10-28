"""
Embeddings configuration classes.

Contains configuration for Google, OpenAI, HuggingFace, and Anthropic embeddings providers.
"""


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

