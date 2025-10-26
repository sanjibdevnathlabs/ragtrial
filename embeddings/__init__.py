"""
Embeddings package - Provider-agnostic embeddings abstraction.

This package provides an ORM-like abstraction over different embedding providers.
Switch providers by changing config only - no code changes needed!

Usage:
    from embeddings import create_embeddings
    
    # Automatically picks correct provider from config
    embeddings = create_embeddings(app_config)
    
    # Use uniform API regardless of provider
    vectors = embeddings.embed_documents(["text1", "text2"])
    query_vector = embeddings.embed_query("search query")
"""

from embeddings.factory import create_embeddings

__all__ = ["create_embeddings"]

