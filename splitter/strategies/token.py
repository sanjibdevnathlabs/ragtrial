"""
Token-Based Text Splitter Strategy.

Splits documents based on token count using LangChain's TokenTextSplitter.
This ensures chunks fit within embedding model token limits.
"""

from typing import List

from langchain_text_splitters import TokenTextSplitter
from langchain_core.documents import Document


class TokenSplitterStrategy:
    """Strategy for splitting documents by token count.
    
    Uses TokenTextSplitter from LangChain to split documents into chunks
    based on token count rather than character count. This is important
    because embedding models have token limits (not character limits).
    
    Attributes:
        chunk_size: Maximum number of tokens per chunk
        chunk_overlap: Number of tokens to overlap between chunks
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 100):
        """Initialize token-based splitter.
        
        Args:
            chunk_size: Maximum tokens per chunk (default: 512)
            chunk_overlap: Tokens to overlap between chunks (default: 100)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into token-based chunks.
        
        Args:
            documents: List of Document objects to split
            
        Returns:
            List of Document objects representing chunks.
            Each chunk preserves the original document's metadata.
            
        Raises:
            Exception: If splitting fails
        """
        return self._splitter.split_documents(documents)

