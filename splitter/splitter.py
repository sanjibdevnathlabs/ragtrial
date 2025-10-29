"""
Document Splitter - Main Interface.

Provides a simple, unified interface for splitting documents into chunks.
Implements the Facade pattern to hide complexity of strategies and factory.
"""

import trace.codes as codes
from typing import List

from langchain_core.documents import Document

import constants
from logger.setup import get_logger
from splitter.factory import SplitterFactory
from splitter.validators import SplitterParameterValidator

logger = get_logger(__name__)


class DocumentSplitter:
    """Main document splitter facade.

    Provides a simple interface for splitting documents into smaller chunks.
    Delegates validation and splitting to specialized components.

    This is the main entry point for text splitting - clients should
    use this class rather than interacting with strategies directly.

    Usage:
        splitter = DocumentSplitter(chunk_size=512, chunk_overlap=100)
        chunks = splitter.split_documents(documents)
    """

    def __init__(
        self,
        chunk_size: int = constants.DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = constants.DEFAULT_CHUNK_OVERLAP,
        splitter_type: str = constants.SPLITTER_TYPE_TOKEN,
    ):
        """Initialize document splitter.

        Args:
            chunk_size: Maximum size per chunk (default: 512 tokens)
            chunk_overlap: Overlap between chunks (default: 100 tokens)
            splitter_type: Type of splitter to use (default: 'token')

        Raises:
            ValueError: If parameters are invalid
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter_type = splitter_type

        self._log_initialization()

        # Create splitter strategy via factory (validates parameters)
        self._splitter = SplitterFactory.create(
            splitter_type=splitter_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks.

        Main method for splitting documents. Handles validation,
        splitting, and logging.

        Args:
            documents: List of Document objects to split

        Returns:
            List of Document objects representing chunks.
            Each chunk preserves the original document's metadata.

        Raises:
            ValueError: If documents list is empty
        """
        # Validate (raises if empty)
        SplitterParameterValidator.validate_documents_not_empty(documents)

        # Log splitting start
        self._log_splitting_start(documents)

        # Split using strategy
        chunks = self._split_with_strategy(documents)

        # Log success
        self._log_splitting_success(documents, chunks)

        return chunks

    def _log_initialization(self) -> None:
        """Log splitter initialization."""
        logger.info(
            codes.SPLITTER_INITIALIZED,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            splitter_type=self.splitter_type,
        )

    def _log_splitting_start(self, documents: List[Document]) -> None:
        """Log splitting operation start.

        Args:
            documents: Documents being split
        """
        logger.info(
            codes.SPLITTER_SPLITTING,
            document_count=len(documents),
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def _split_with_strategy(self, documents: List[Document]) -> List[Document]:
        """Split documents using the configured strategy.

        Delegates to the strategy created by factory.

        Args:
            documents: List of documents to split

        Returns:
            List of document chunks

        Raises:
            Exception: If splitting fails
        """
        try:
            return self._splitter.split_documents(documents)

        except Exception as e:
            logger.error(
                codes.SPLITTER_ERROR, error=str(e), document_count=len(documents)
            )
            raise

    def _log_splitting_success(
        self, documents: List[Document], chunks: List[Document]
    ) -> None:
        """Log successful splitting operation.

        Args:
            documents: Original documents
            chunks: Resulting chunks
        """
        logger.info(
            codes.SPLITTER_SPLIT_COMPLETE,
            input_documents=len(documents),
            output_chunks=len(chunks),
        )

    def get_chunk_size(self) -> int:
        """Get configured chunk size.

        Returns:
            Chunk size in tokens
        """
        return self.chunk_size

    def get_chunk_overlap(self) -> int:
        """Get configured chunk overlap.

        Returns:
            Chunk overlap in tokens
        """
        return self.chunk_overlap

    def get_splitter_type(self) -> str:
        """Get configured splitter type.

        Returns:
            Splitter type identifier
        """
        return self.splitter_type
