"""
Document Loader Module.

Provides document loading capabilities with support for multiple file formats.
Follows clean architecture with protocol-based interfaces, factory pattern,
and strategy pattern for extensibility.

Public API:
    - DocumentLoader: Main facade for loading documents
    - LoaderFactory: Factory for creating loader strategies
    - LoaderProtocol: Interface for loader implementations
    
Usage:
    from loader import DocumentLoader
    
    loader = DocumentLoader()
    documents = loader.load_document("path/to/file.pdf")
"""

from loader.base import LoaderProtocol
from loader.factory import LoaderFactory
from loader.loader import DocumentLoader

__all__ = [
    "DocumentLoader",
    "LoaderFactory",
    "LoaderProtocol",
]

