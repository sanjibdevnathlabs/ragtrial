"""
Markdown Document Loader Strategy.

Loads Markdown (.md) documents.
"""

from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


class MarkdownLoaderStrategy:
    """Strategy for loading Markdown documents.

    Uses TextLoader for fast, lightweight markdown loading.
    Markdown is already structured text, so heavy NLP parsing is unnecessary.
    """

    def __init__(self, file_path: str):
        """Initialize Markdown loader.

        Args:
            file_path: Path to Markdown file
        """
        self.file_path = file_path
        self._loader = TextLoader(file_path)

    def load(self) -> List[Document]:
        """Load Markdown document.

        Returns:
            List of Document objects

        Raises:
            Exception: If Markdown loading fails
        """
        return self._loader.load()
