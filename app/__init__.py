"""
Application package for RAG applications.

Provides retrieval-augmented generation capabilities using LangChain.
"""

from app.simple_rag.chain import RAGChain
from app.simple_rag.base import RAGProtocol

__all__ = [
    "RAGChain",
    "RAGProtocol",
]

