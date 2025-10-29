"""
LLM (Large Language Model) configuration classes.

Contains configuration for Google (Gemini), OpenAI (GPT), and Anthropic (Claude) LLMs.
"""


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
