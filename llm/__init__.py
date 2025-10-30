"""
LLM (Large Language Model) module.

Provides factory for creating LLM instances across different providers.
Follows the same pattern as embeddings and vectorstore modules.
"""

from llm.base import LLMProtocol
from llm.factory import create_llm

__all__ = ["LLMProtocol", "create_llm"]

