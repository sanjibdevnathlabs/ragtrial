"""
Factory for creating vector store providers.

The factory automatically instantiates the correct vectorstore implementation
based on configuration, enabling zero-code-change provider switching.
"""

from typing import TYPE_CHECKING

from vectorstore.base import VectorStoreProtocol
from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


def create_vectorstore(
    config: "Config",
    embeddings: EmbeddingsProtocol
) -> VectorStoreProtocol:
    """
    Create a vector store provider based on configuration.
    
    This factory function reads config.vectorstore.provider and instantiates
    the appropriate implementation. To switch providers, just change the
    config - no code changes needed!
    
    Args:
        config: Application configuration object
        embeddings: Embeddings provider (for generating vectors)
        
    Returns:
        A vectorstore implementation following VectorStoreProtocol
        
    Raises:
        ValueError: If provider is unknown or not supported
        
    Example:
        # In config: provider = "chroma"
        vectorstore = create_vectorstore(config, embeddings)
        # Returns ChromaVectorStore instance
        
        # Change config: provider = "pinecone"
        vectorstore = create_vectorstore(config, embeddings)
        # Returns PineconeVectorStore instance - same code!
    """
    provider = config.vectorstore.provider.lower()
    
    logger.info(
        codes.VECTORSTORE_FACTORY_CREATING,
        provider=provider
    )
    
    if provider == "chroma":
        from vectorstore.implementations.chroma import ChromaVectorStore
        return ChromaVectorStore(config, embeddings)
    
    elif provider == "pinecone":
        from vectorstore.implementations.pinecone import PineconeVectorStore
        return PineconeVectorStore(config, embeddings)
    
    elif provider == "qdrant":
        from vectorstore.implementations.qdrant import QdrantVectorStore
        return QdrantVectorStore(config, embeddings)
    
    elif provider == "weaviate":
        from vectorstore.implementations.weaviate import WeaviateVectorStore
        return WeaviateVectorStore(config, embeddings)
    
    else:
        error_msg = f"{codes.MSG_VECTORSTORE_PROVIDER_UNKNOWN}: {provider}"
        logger.error(
            codes.VECTORSTORE_PROVIDER_UNKNOWN,
            provider=provider,
            message=error_msg
        )
        raise ValueError(error_msg)

