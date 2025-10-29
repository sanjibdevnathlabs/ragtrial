"""
Document Loader Protocol.

Defines the interface that all document loader strategies must implement.
This follows the same pattern as embeddings/base.py and vectorstore/base.py.
"""

from typing import List, Protocol

from langchain_core.documents import Document


class LoaderProtocol(Protocol):
    """Protocol defining interface for document loaders.

    All loader implementations must provide a load() method that returns
    a list of Document objects.

    This protocol allows for type-safe, plug-and-play loader strategies.
    """

    def load(self) -> List[Document]:
        """Load and return documents.

        Returns:
            List of Document objects loaded from the source

        Raises:
            Exception: If loading fails
        """
        ...
