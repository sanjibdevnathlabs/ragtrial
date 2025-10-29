"""
RAG Protocol Interface.

Defines the contract for retrieval-augmented generation implementations.
"""

from typing import Any, Dict, Protocol


class RAGProtocol(Protocol):
    """
    Protocol for retrieval-augmented generation chains.

    Implementations must provide a query method that accepts a user question
    and returns an answer with source citations.
    """

    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a query and return an answer with sources.

        Args:
            question: User's question string

        Returns:
            Dictionary containing:
                - answer: Generated answer text
                - sources: List of source documents with metadata
                - query: Original question
                - retrieval_count: Number of documents retrieved
                - has_answer: Boolean indicating if answer was generated

        Raises:
            ValueError: If question is empty or invalid
        """
        ...
