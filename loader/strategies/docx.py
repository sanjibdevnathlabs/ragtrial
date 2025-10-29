"""
DOCX Document Loader Strategy.

Loads Microsoft Word (.docx) documents.
"""

from typing import List

from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.documents import Document


class DocxLoaderStrategy:
    """Strategy for loading DOCX documents.

    Uses Docx2txtLoader from LangChain to parse Word documents.
    """

    def __init__(self, file_path: str):
        """Initialize DOCX loader.

        Args:
            file_path: Path to DOCX file
        """
        self.file_path = file_path
        self._loader = Docx2txtLoader(file_path)

    def load(self) -> List[Document]:
        """Load DOCX document.

        Returns:
            List of Document objects

        Raises:
            Exception: If DOCX loading fails
        """
        return self._loader.load()
