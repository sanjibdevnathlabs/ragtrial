"""
Text Document Loader Strategy.

Loads plain text (.txt) documents.
"""

from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


class TextLoaderStrategy:
    """Strategy for loading plain text documents.
    
    Uses TextLoader from LangChain to parse text files with UTF-8 encoding.
    """

    def __init__(self, file_path: str):
        """Initialize text loader.
        
        Args:
            file_path: Path to text file
        """
        self.file_path = file_path
        self._loader = TextLoader(file_path, encoding="utf-8")

    def load(self) -> List[Document]:
        """Load text document.
        
        Returns:
            List of Document objects (typically one document)
            
        Raises:
            Exception: If text loading fails (encoding issues, etc.)
        """
        return self._loader.load()

