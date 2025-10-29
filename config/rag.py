"""
RAG (Retrieval-Augmented Generation) configuration classes.

Contains configuration for RAG chain and Google API credentials.
"""

from config.llm import AnthropicLLMConfig, GoogleLLMConfig, OpenAILLMConfig


class GoogleConfig:
    """Holds settings from the [google] TOML section"""

    api_key: str = None


class RAGConfig:
    """RAG (Retrieval-Augmented Generation) configuration"""

    provider: str = "google"
    retrieval_k: int = 5
    google: GoogleLLMConfig = None
    openai: OpenAILLMConfig = None
    anthropic: AnthropicLLMConfig = None
