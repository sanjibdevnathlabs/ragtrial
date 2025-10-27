"""
JSON Document Loader Strategy.

Loads JSON (.json) documents.
"""

from typing import List

from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document


class JSONLoaderStrategy:
    """Strategy for loading JSON documents.
    
    Uses JSONLoader from LangChain to parse JSON files.
    Uses jq_schema to extract content from JSON structure.
    """

    def __init__(self, file_path: str):
        """Initialize JSON loader.
        
        Args:
            file_path: Path to JSON file
        """
        self.file_path = file_path
        self._loader = JSONLoader(
            file_path=file_path,
            jq_schema=".",
            text_content=False
        )

    def load(self) -> List[Document]:
        """Load JSON document.
        
        Returns:
            List of Document objects
            
        Raises:
            Exception: If JSON loading fails
        """
        return self._loader.load()

