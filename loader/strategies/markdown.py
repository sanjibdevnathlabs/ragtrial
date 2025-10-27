"""
Markdown Document Loader Strategy.

Loads Markdown (.md) documents.
"""

from typing import List

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document


class MarkdownLoaderStrategy:
    """Strategy for loading Markdown documents.
    
    Uses UnstructuredMarkdownLoader from LangChain to parse markdown files.
    """

    def __init__(self, file_path: str):
        """Initialize Markdown loader.
        
        Args:
            file_path: Path to Markdown file
        """
        self.file_path = file_path
        self._loader = UnstructuredMarkdownLoader(file_path)

    def load(self) -> List[Document]:
        """Load Markdown document.
        
        Returns:
            List of Document objects
            
        Raises:
            Exception: If Markdown loading fails
        """
        return self._loader.load()

