"""
Document Loader Factory.

Factory for creating appropriate document loader strategies based on file type.
Follows the same pattern as embeddings/factory.py and vectorstore/factory.py.
"""

from pathlib import Path
from typing import List

import constants
import trace.codes as codes
from loader.base import LoaderProtocol
from loader.strategies import (
    CSVLoaderStrategy,
    DocxLoaderStrategy,
    JSONLoaderStrategy,
    MarkdownLoaderStrategy,
    PDFLoaderStrategy,
    TextLoaderStrategy,
)
from logger.setup import get_logger

logger = get_logger(__name__)


class LoaderFactory:
    """Factory for creating document loader strategies.
    
    Maps file extensions to appropriate loader strategy classes.
    Follows the Factory Method pattern with Open/Closed Principle.
    """

    # Map file extensions to loader strategy classes
    _STRATEGY_MAP = {
        constants.EXT_PDF: PDFLoaderStrategy,
        constants.EXT_TXT: TextLoaderStrategy,
        constants.EXT_MD: MarkdownLoaderStrategy,
        constants.EXT_DOCX: DocxLoaderStrategy,
        constants.EXT_CSV: CSVLoaderStrategy,
        constants.EXT_JSON: JSONLoaderStrategy,
    }

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported extensions (e.g., ['.pdf', '.txt', ...])
        """
        return list(cls._STRATEGY_MAP.keys())

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Check if file type is supported.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file type is supported, False otherwise
        """
        extension = file_path.suffix.lower()
        return extension in cls._STRATEGY_MAP

    @classmethod
    def create(cls, file_path: Path) -> LoaderProtocol:
        """Create appropriate loader strategy for file type.
        
        Factory method that instantiates the correct strategy based on
        file extension. Follows Open/Closed Principle - new strategies
        can be added to _STRATEGY_MAP without modifying this method.
        
        Args:
            file_path: Path to file
            
        Returns:
            Loader strategy instance
            
        Raises:
            ValueError: If file type is not supported
        """
        extension = file_path.suffix.lower()

        if extension not in cls._STRATEGY_MAP:
            error_msg = f"{constants.ERROR_UNSUPPORTED_FORMAT}: {extension}"
            logger.error(
                codes.LOADER_UNSUPPORTED_FORMAT,
                extension=extension,
                supported=cls.get_supported_extensions()
            )
            raise ValueError(error_msg)

        strategy_class = cls._STRATEGY_MAP[extension]
        return strategy_class(str(file_path))

