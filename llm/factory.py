"""
Factory for creating LLM providers.

The factory automatically instantiates the correct LLM implementation
based on configuration, enabling zero-code-change provider switching.
Follows the same pattern as embeddings and vectorstore factories.
"""

from trace import codes
from typing import TYPE_CHECKING, Any

import constants
from llm.base import LLMProtocol
from logger import get_logger

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


def create_llm(config: "Config", **override_kwargs: Any) -> LLMProtocol:
    """
    Create an LLM provider based on configuration.

    Uses a provider-based factory pattern for clean, maintainable code that follows
    the Open/Closed Principle. To add a new provider, simply add implementation here.

    Args:
        config: Application configuration object
        **override_kwargs: Optional keyword arguments to override config values
                          (e.g., temperature=0, max_tokens=10 for health checks)

    Returns:
        An LLM instance following LLMProtocol (ChatGoogleGenerativeAI, ChatOpenAI, or ChatAnthropic)

    Raises:
        ValueError: If provider is unknown or not supported

    Example:
        # Standard usage
        llm = create_llm(config)

        # Health check usage with minimal tokens
        llm = create_llm(config, temperature=0, max_tokens=10)
    """
    provider = config.rag.provider.lower()

    logger.info(codes.LLM_FACTORY_CREATING, provider=provider)

    if provider == constants.LLM_PROVIDER_GOOGLE:
        return _create_google_llm(config, **override_kwargs)

    if provider == constants.LLM_PROVIDER_OPENAI:
        return _create_openai_llm(config, **override_kwargs)

    if provider == constants.LLM_PROVIDER_ANTHROPIC:
        return _create_anthropic_llm(config, **override_kwargs)

    error_msg = f"Unsupported LLM provider: {provider}"
    logger.error(codes.LLM_PROVIDER_UNKNOWN, provider=provider, message=error_msg)
    raise ValueError(error_msg)


def _create_google_llm(config: "Config", **override_kwargs: Any):
    """Create Google Gemini LLM instance."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm_config = config.rag.google

    kwargs = {
        "model": llm_config.model,
        "temperature": llm_config.temperature,
        "max_output_tokens": llm_config.max_tokens,
    }

    # Apply overrides (for health checks, testing, etc.)
    kwargs.update(override_kwargs)

    # Only pass API key if explicitly set
    if llm_config.api_key:
        kwargs["google_api_key"] = llm_config.api_key

    return ChatGoogleGenerativeAI(**kwargs)


def _create_openai_llm(config: "Config", **override_kwargs: Any):
    """Create OpenAI GPT LLM instance."""
    from langchain_openai import ChatOpenAI

    llm_config = config.rag.openai

    kwargs = {
        "model": llm_config.model,
        "temperature": llm_config.temperature,
        "max_tokens": llm_config.max_tokens,
    }

    # Apply overrides (for health checks, testing, etc.)
    kwargs.update(override_kwargs)

    # Only pass API key if explicitly set
    if llm_config.api_key:
        kwargs["api_key"] = llm_config.api_key

    return ChatOpenAI(**kwargs)


def _create_anthropic_llm(config: "Config", **override_kwargs: Any):
    """Create Anthropic Claude LLM instance."""
    from langchain_anthropic import ChatAnthropic

    llm_config = config.rag.anthropic

    kwargs = {
        "model": llm_config.model,
        "temperature": llm_config.temperature,
        "max_tokens": llm_config.max_tokens,
    }

    # Apply overrides (for health checks, testing, etc.)
    kwargs.update(override_kwargs)

    # Only pass API key if explicitly set
    if llm_config.api_key:
        kwargs["anthropic_api_key"] = llm_config.api_key

    return ChatAnthropic(**kwargs)

