"""
PDF Document Loader Strategy.

Loads PDF documents using LangChain's PyPDFLoader.
"""

from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class PDFLoaderStrategy:
    """Strategy for loading PDF documents.
    
    Uses PyPDFLoader from LangChain to parse PDF files.
    """

    def __init__(self, file_path: str):
        """Initialize PDF loader.
        
        Args:
            file_path: Path to PDF file
        """
        self.file_path = file_path
        self._loader = PyPDFLoader(file_path)

    def load(self) -> List[Document]:
        """Load PDF document.
        
        Returns:
            List of Document objects (one per page typically)
            
        Raises:
            Exception: If PDF loading fails (corrupted file, etc.)
        """
        return self._loader.load()

