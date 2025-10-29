"""
Vectorstore package - Provider-agnostic vector database abstraction.

This package provides an ORM-like abstraction over different vector databases.
Switch providers by changing config only - no code changes needed!

Usage:
    from embeddings import create_embeddings
    from vectorstore import create_vectorstore

    # Initialize (automatically picks correct provider from config)
    embeddings = create_embeddings(app_config)
    vectorstore = create_vectorstore(app_config, embeddings)

    # Use uniform API regardless of provider
    vectorstore.add_documents(
        texts=["doc 1", "doc 2"],
        metadatas=[{"source": "a.pdf"}, {"source": "b.pdf"}],
        ids=["1", "2"]
    )

    results = vectorstore.query("search query", n_results=5)
"""

from vectorstore.factory import create_vectorstore

__all__ = ["create_vectorstore"]
