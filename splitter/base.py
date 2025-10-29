"""
Text Splitter Protocol.

Defines the interface that all text splitter strategies must implement.
Follows the same pattern as loader/base.py.
"""

from typing import List, Protocol

from langchain_core.documents import Document


class SplitterProtocol(Protocol):
    """Protocol defining interface for text splitters.

    All splitter implementations must provide a split_documents() method
    that takes documents and returns them split into smaller chunks.

    This protocol allows for type-safe, plug-and-play splitter strategies.
    """

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks.

        Args:
            documents: List of Document objects to split

        Returns:
            List of Document objects representing chunks

        Raises:
            Exception: If splitting fails
        """
        ...
