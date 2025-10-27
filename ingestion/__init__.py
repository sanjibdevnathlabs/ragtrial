"""
Document Ingestion Module.

Orchestrates the complete document ingestion pipeline:
1. Load documents from various file formats (loader module)
2. Split documents into chunks (splitter module)
3. Generate embeddings (embeddings module)
4. Store in vector database (vectorstore module)

This module acts as the orchestrator for the complete ingestion workflow.
Use the individual modules directly for granular control:
    - loader.DocumentLoader for loading documents
    - splitter.DocumentSplitter for splitting text
    
Usage:
    # Import from source modules directly
    from loader import DocumentLoader
    from splitter import DocumentSplitter
    
    # Load documents
    loader = DocumentLoader()
    documents = loader.load_document("path/to/file.pdf")
    
    # Split into chunks
    splitter = DocumentSplitter(chunk_size=512, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
"""

# This module currently contains orchestration logic only
# Individual components are imported directly from their modules:
#   - from loader import DocumentLoader
#   - from splitter import DocumentSplitter

__all__ = []  # No re-exports - use source modules directly
