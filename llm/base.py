"""
Base protocol (interface) for LLM providers.

All LLM implementations must follow this protocol to ensure
a uniform API regardless of provider (Google, OpenAI, Anthropic).
"""

from typing import Any, Protocol


class LLMProtocol(Protocol):
    """
    Abstract interface that all LLM providers must implement.

    This protocol defines the contract for LLM operations,
    ensuring consistent behavior across Google Gemini, OpenAI GPT, Anthropic Claude, etc.

    All LangChain chat models (ChatGoogleGenerativeAI, ChatOpenAI, ChatAnthropic)
    implement this protocol through their .invoke() method.
    """

    def invoke(self, input: str, **kwargs: Any) -> Any:
        """
        Generate response for the given input.

        This is the primary method for LLM interaction. All LangChain chat models
        implement this method with consistent behavior.

        Args:
            input: Text prompt or message to send to the LLM
            **kwargs: Additional provider-specific parameters

        Returns:
            Response object with .content attribute containing the generated text

        Example:
            llm = create_llm(config)
            response = llm.invoke("What is RAG?")
            print(response.content)  # "RAG stands for..."
        """
        ...

