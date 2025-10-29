"""
Document Splitter Module.

Provides text splitting capabilities for chunking documents into smaller pieces.
Follows clean architecture with protocol-based interfaces, factory pattern,
and strategy pattern for extensibility.

Public API:
    - DocumentSplitter: Main facade for splitting documents
    - SplitterFactory: Factory for creating splitter strategies
    - SplitterProtocol: Interface for splitter implementations

Usage:
    from splitter import DocumentSplitter

    splitter = DocumentSplitter(chunk_size=512, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
"""

from splitter.base import SplitterProtocol
from splitter.factory import SplitterFactory
from splitter.splitter import DocumentSplitter

__all__ = [
    "DocumentSplitter",
    "SplitterFactory",
    "SplitterProtocol",
]
