"""
Text Splitter Factory.

Factory for creating appropriate text splitter strategies.
Follows the same pattern as loader/factory.py.
"""

import trace.codes as codes

import constants
from logger.setup import get_logger
from splitter.base import SplitterProtocol
from splitter.strategies import TokenSplitterStrategy
from splitter.validators import SplitterParameterValidator

logger = get_logger(__name__)


class SplitterFactory:
    """Factory for creating text splitter strategies.

    Currently supports token-based splitting. Can be extended to support
    recursive, character-based, or custom splitting strategies.

    Follows the Factory Method pattern with Open/Closed Principle.
    """

    # Map splitter types to strategy classes
    _STRATEGY_MAP = {
        constants.SPLITTER_TYPE_TOKEN: TokenSplitterStrategy,
        # Future: Add more splitter types
        # constants.SPLITTER_TYPE_RECURSIVE: RecursiveSplitterStrategy,
        # constants.SPLITTER_TYPE_CHARACTER: CharacterSplitterStrategy,
    }

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported splitter types.

        Returns:
            List of supported splitter type identifiers
        """
        return list(cls._STRATEGY_MAP.keys())

    @classmethod
    def is_supported(cls, splitter_type: str) -> bool:
        """Check if splitter type is supported.

        Args:
            splitter_type: Type identifier (e.g., 'token')

        Returns:
            True if splitter type is supported, False otherwise
        """
        return splitter_type in cls._STRATEGY_MAP

    @classmethod
    def create(
        cls,
        splitter_type: str = constants.SPLITTER_TYPE_TOKEN,
        chunk_size: int = constants.DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = constants.DEFAULT_CHUNK_OVERLAP,
    ) -> SplitterProtocol:
        """Create appropriate splitter strategy.

        Factory method that instantiates the correct strategy based on
        splitter type. Validates parameters and creates strategy instance.

        Args:
            splitter_type: Type of splitter ('token', 'recursive', etc.)
            chunk_size: Maximum size per chunk
            chunk_overlap: Overlap between chunks

        Returns:
            Splitter strategy instance

        Raises:
            ValueError: If splitter type is not supported or parameters invalid
        """
        # Validate parameters (raises if invalid)
        SplitterParameterValidator.validate_all(chunk_size, chunk_overlap)

        # Check if splitter type is supported
        if splitter_type not in cls._STRATEGY_MAP:
            error_msg = f"Unsupported splitter type: {splitter_type}"
            logger.error(
                codes.SPLITTER_ERROR,
                splitter_type=splitter_type,
                supported=cls.get_supported_types(),
            )
            raise ValueError(error_msg)

        # Create strategy
        strategy_class = cls._STRATEGY_MAP[splitter_type]
        return strategy_class(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
