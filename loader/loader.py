"""
Document Loader - Main Interface.

Provides a simple, unified interface for loading documents of various types.
Implements the Facade pattern to hide complexity of strategies and factory.
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document

import trace.codes as codes
from loader.factory import LoaderFactory
from loader.metadata import DocumentMetadataEnricher
from loader.validators import LoaderValidator
from logger.setup import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """Main document loader facade.
    
    Provides a simple interface for loading documents of various types.
    Delegates validation, loading, and enrichment to specialized components.
    
    This is the main entry point for document loading - clients should
    use this class rather than interacting with strategies directly.
    
    Usage:
        loader = DocumentLoader()
        documents = loader.load_document("path/to/file.pdf")
    """

    def __init__(self):
        """Initialize document loader."""
        logger.info(codes.MSG_LOADER_INITIALIZED)

    def load_document(self, file_path: str | Path) -> List[Document]:
        """Load document from file.
        
        Main method for loading documents. Handles validation, loading,
        and metadata enrichment through specialized components.
        
        Args:
            file_path: Path to document file (string or Path object)
            
        Returns:
            List of Document objects with enriched metadata
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file type is not supported or document is empty
        """
        path = self._normalize_path(file_path)
        
        # Validate (raises if invalid)
        self._validate(path)
        
        # Log loading start
        self._log_loading_start(path)
        
        # Load using strategy
        documents = self._load_with_strategy(path)
        
        # Validate loaded documents
        LoaderValidator.validate_documents_loaded(documents, path)
        
        # Enrich metadata
        enriched_documents = DocumentMetadataEnricher.enrich(documents, path)
        
        # Log success
        self._log_loading_success(path, enriched_documents)
        
        return enriched_documents

    def _normalize_path(self, file_path: str | Path) -> Path:
        """Normalize file path to Path object.
        
        Args:
            file_path: String or Path object
            
        Returns:
            Path object
        """
        return Path(file_path) if isinstance(file_path, str) else file_path

    def _validate(self, path: Path) -> None:
        """Validate file exists and is supported.
        
        Args:
            path: Path to file
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file type is not supported
        """
        LoaderValidator.validate_file_exists(path)
        LoaderValidator.validate_file_supported(path, LoaderFactory.is_supported)

    def _log_loading_start(self, path: Path) -> None:
        """Log loading operation start.
        
        Args:
            path: Path to file being loaded
        """
        logger.info(
            codes.LOADER_LOADING_FILE,
            file_path=str(path),
            file_type=path.suffix
        )

    def _load_with_strategy(self, path: Path) -> List[Document]:
        """Load document using appropriate strategy.
        
        Delegates to factory to create strategy, then calls load().
        
        Args:
            path: Path to file
            
        Returns:
            List of Document objects
            
        Raises:
            Exception: If loading fails
        """
        try:
            loader = LoaderFactory.create(path)
            return loader.load()

        except Exception as e:
            logger.error(
                codes.LOADER_LOADING_ERROR,
                file_path=str(path),
                error=str(e)
            )
            raise

    def _log_loading_success(
        self,
        path: Path,
        documents: List[Document]
    ) -> None:
        """Log successful loading operation.
        
        Args:
            path: Path to loaded file
            documents: Loaded documents
        """
        logger.info(
            codes.LOADER_FILE_LOADED,
            file_path=str(path),
            document_count=len(documents)
        )

    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported extensions
        """
        return LoaderFactory.get_supported_extensions()

    def is_supported_file(self, file_path: str | Path) -> bool:
        """Check if file type is supported.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file type is supported, False otherwise
        """
        path = self._normalize_path(file_path)
        return LoaderFactory.is_supported(path)

