"""
Base protocol (interface) for embeddings providers.

All embedding implementations must follow this protocol to ensure
a uniform API regardless of provider.
"""

from typing import List, Protocol


class EmbeddingsProtocol(Protocol):
    """
    Abstract interface that all embedding providers must implement.

    This protocol defines the contract for embedding operations,
    ensuring consistent behavior across Google, OpenAI, HuggingFace, etc.
    """

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)

        Example:
            texts = ["doc 1", "doc 2"]
            vectors = embeddings.embed_documents(texts)
            # [[0.1, 0.2, ...], [0.3, 0.4, ...]]
        """
        ...

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.

        Some providers optimize differently for queries vs documents.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector as list of floats

        Example:
            query = "What is RAG?"
            vector = embeddings.embed_query(query)
            # [0.1, 0.2, 0.3, ...]
        """
        ...

    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings this provider generates.

        Returns:
            Integer dimension (e.g., 768, 1536, 3072)
        """
        ...
