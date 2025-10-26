"""
Factory for creating vector store providers.

The factory automatically instantiates the correct vectorstore implementation
based on configuration, enabling zero-code-change provider switching.
"""

import importlib
from typing import TYPE_CHECKING

from vectorstore.base import VectorStoreProtocol
from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


PROVIDER_MAP = {
    "chroma": ("vectorstore.implementations.chroma", "ChromaVectorStore"),
    "pinecone": ("vectorstore.implementations.pinecone", "PineconeVectorStore"),
    "qdrant": ("vectorstore.implementations.qdrant", "QdrantVectorStore"),
    "weaviate": ("vectorstore.implementations.weaviate", "WeaviateVectorStore"),
}


def create_vectorstore(
    config: "Config",
    embeddings: EmbeddingsProtocol
) -> VectorStoreProtocol:
    """
    Create a vector store provider based on configuration.
    
    Uses a provider mapping dictionary for clean, maintainable code that follows
    the Open/Closed Principle. To add a new provider, simply add an entry to
    PROVIDER_MAP.
    
    Args:
        config: Application configuration object
        embeddings: Embeddings provider (for generating vectors)
        
    Returns:
        A vectorstore implementation following VectorStoreProtocol
        
    Raises:
        ValueError: If provider is unknown or not supported
        
    Example:
        vectorstore = create_vectorstore(config, embeddings)
        # Automatically instantiates correct provider from config
    """
    provider = config.vectorstore.provider.lower()
    
    logger.info(codes.VECTORSTORE_FACTORY_CREATING, provider=provider)
    
    if provider not in PROVIDER_MAP:
        error_msg = f"{codes.MSG_VECTORSTORE_PROVIDER_UNKNOWN}: {provider}"
        logger.error(codes.VECTORSTORE_PROVIDER_UNKNOWN, provider=provider, message=error_msg)
        raise ValueError(error_msg)
    
    module_path, class_name = PROVIDER_MAP[provider]
    module = importlib.import_module(module_path)
    provider_class = getattr(module, class_name)
    
    return provider_class(config, embeddings)

