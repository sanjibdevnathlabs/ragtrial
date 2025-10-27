"""
CSV Document Loader Strategy.

Loads CSV (.csv) documents.
"""

from typing import List

from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document


class CSVLoaderStrategy:
    """Strategy for loading CSV documents.
    
    Uses CSVLoader from LangChain to parse CSV files.
    Each row becomes a separate document.
    """

    def __init__(self, file_path: str):
        """Initialize CSV loader.
        
        Args:
            file_path: Path to CSV file
        """
        self.file_path = file_path
        self._loader = CSVLoader(file_path)

    def load(self) -> List[Document]:
        """Load CSV document.
        
        Returns:
            List of Document objects (one per row)
            
        Raises:
            Exception: If CSV loading fails
        """
        return self._loader.load()

