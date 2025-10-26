"""
Factory for creating embeddings providers.

The factory automatically instantiates the correct embeddings implementation
based on configuration, enabling zero-code-change provider switching.
"""

from typing import TYPE_CHECKING

from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


def create_embeddings(config: "Config") -> EmbeddingsProtocol:
    """
    Create an embeddings provider based on configuration.
    
    This factory function reads config.embeddings.provider and instantiates
    the appropriate implementation. To switch providers, just change the
    config - no code changes needed!
    
    Args:
        config: Application configuration object
        
    Returns:
        An embeddings implementation following EmbeddingsProtocol
        
    Raises:
        ValueError: If provider is unknown or not supported
        
    Example:
        # In config: provider = "google"
        embeddings = create_embeddings(config)
        # Returns GoogleEmbeddings instance
        
        # Change config: provider = "openai"
        embeddings = create_embeddings(config)
        # Returns OpenAIEmbeddings instance - same code!
    """
    provider = config.embeddings.provider.lower()
    
    logger.info(
        codes.EMBEDDINGS_FACTORY_CREATING,
        provider=provider
    )
    
    if provider == "google":
        from embeddings.implementations.google import GoogleEmbeddings
        return GoogleEmbeddings(config)
    
    elif provider == "openai":
        from embeddings.implementations.openai import OpenAIEmbeddings
        return OpenAIEmbeddings(config)
    
    elif provider == "huggingface":
        from embeddings.implementations.huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(config)
    
    elif provider == "anthropic":
        from embeddings.implementations.anthropic import AnthropicEmbeddings
        return AnthropicEmbeddings(config)
    
    else:
        error_msg = f"{codes.MSG_EMBEDDINGS_PROVIDER_UNKNOWN}: {provider}"
        logger.error(
            codes.EMBEDDINGS_PROVIDER_UNKNOWN,
            provider=provider,
            message=error_msg
        )
        raise ValueError(error_msg)

