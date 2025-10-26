"""
Factory for creating embeddings providers.

The factory automatically instantiates the correct embeddings implementation
based on configuration, enabling zero-code-change provider switching.
"""

import importlib
from typing import TYPE_CHECKING

from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


PROVIDER_MAP = {
    "google": ("embeddings.implementations.google", "GoogleEmbeddings"),
    "openai": ("embeddings.implementations.openai", "OpenAIEmbeddings"),
    "huggingface": ("embeddings.implementations.huggingface", "HuggingFaceEmbeddings"),
    "anthropic": ("embeddings.implementations.anthropic", "AnthropicEmbeddings"),
}


def create_embeddings(config: "Config") -> EmbeddingsProtocol:
    """
    Create an embeddings provider based on configuration.
    
    Uses a provider mapping dictionary for clean, maintainable code that follows
    the Open/Closed Principle. To add a new provider, simply add an entry to
    PROVIDER_MAP.
    
    Args:
        config: Application configuration object
        
    Returns:
        An embeddings implementation following EmbeddingsProtocol
        
    Raises:
        ValueError: If provider is unknown or not supported
        
    Example:
        embeddings = create_embeddings(config)
        # Automatically instantiates correct provider from config
    """
    provider = config.embeddings.provider.lower()
    
    logger.info(codes.EMBEDDINGS_FACTORY_CREATING, provider=provider)
    
    if provider not in PROVIDER_MAP:
        error_msg = f"{codes.MSG_EMBEDDINGS_PROVIDER_UNKNOWN}: {provider}"
        logger.error(codes.EMBEDDINGS_PROVIDER_UNKNOWN, provider=provider, message=error_msg)
        raise ValueError(error_msg)
    
    module_path, class_name = PROVIDER_MAP[provider]
    module = importlib.import_module(module_path)
    provider_class = getattr(module, class_name)
    
    return provider_class(config)

