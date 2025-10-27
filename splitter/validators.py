"""
Text Splitter Validators.

Handles all validation logic for text splitting parameters.
Follows Single Responsibility Principle - validation only.
"""

from typing import List

from langchain_core.documents import Document

import constants
import trace.codes as codes
from logger.setup import get_logger

logger = get_logger(__name__)


class SplitterParameterValidator:
    """Validator for text splitter parameters.
    
    Centralizes all parameter validation logic with clear, testable methods.
    Each method validates one specific condition.
    """

    @staticmethod
    def validate_chunk_size(chunk_size: int) -> None:
        """Validate chunk size is positive.
        
        Args:
            chunk_size: Maximum size per chunk
            
        Raises:
            ValueError: If chunk size is not positive
        """
        if chunk_size <= 0:
            logger.error(
                codes.SPLITTER_INVALID_PARAMS,
                chunk_size=chunk_size
            )
            raise ValueError(constants.ERROR_INVALID_CHUNK_SIZE)

    @staticmethod
    def validate_overlap(chunk_overlap: int, chunk_size: int) -> None:
        """Validate overlap is valid.
        
        Overlap must be non-negative and less than chunk size.
        
        Args:
            chunk_overlap: Overlap between chunks
            chunk_size: Maximum size per chunk
            
        Raises:
            ValueError: If overlap is invalid
        """
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            logger.error(
                codes.SPLITTER_INVALID_PARAMS,
                chunk_overlap=chunk_overlap,
                chunk_size=chunk_size
            )
            raise ValueError(constants.ERROR_INVALID_OVERLAP)

    @staticmethod
    def validate_all(chunk_size: int, chunk_overlap: int) -> None:
        """Validate all splitting parameters.
        
        Convenience method to validate all parameters at once.
        
        Args:
            chunk_size: Maximum size per chunk
            chunk_overlap: Overlap between chunks
            
        Raises:
            ValueError: If any parameter is invalid
        """
        SplitterParameterValidator.validate_chunk_size(chunk_size)
        SplitterParameterValidator.validate_overlap(chunk_overlap, chunk_size)

    @staticmethod
    def validate_documents_not_empty(documents: List[Document]) -> None:
        """Validate that documents list is not empty.
        
        Args:
            documents: List of documents to validate
            
        Raises:
            ValueError: If documents list is empty
        """
        if not documents:
            logger.warning(codes.SPLITTER_EMPTY_TEXT)
            raise ValueError(constants.ERROR_EMPTY_TEXT)

