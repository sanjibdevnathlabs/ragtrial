"""
Demonstration of the flexible vectorstore and embeddings system.

This script shows how easy it is to use the ORM-like abstraction:
1. Initialize from config
2. Add documents
3. Query for similar documents

To switch providers (e.g., from ChromaDB to Pinecone), just change
the config file - no code changes needed!
"""

import sys
from pathlib import Path

# Add parent directory to path to import from root
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from embeddings import create_embeddings
from vectorstore import create_vectorstore
from logger import setup_logging, get_logger
from trace import codes

# Initialize logger early
logger = get_logger(__name__)

# Initialize configuration
try:
    app_config = Config()
except FileNotFoundError as e:
    logger.error(codes.CONFIG_LOAD_FAILED, error=str(e), message="Configuration file not found")
    sys.exit(1)

# Setup logging
setup_logging(app_config.logging, app_config.app)

def main():
    """Demonstrate vectorstore usage."""
    
    logger.info("=== Vectorstore Demo ===")
    
    # Step 1: Create embeddings provider (automatically picks from config)
    logger.info(f"Creating embeddings provider: {app_config.embeddings.provider}")
    embeddings = create_embeddings(app_config)
    
    # Step 2: Create vectorstore (automatically picks from config)
    logger.info(f"Creating vectorstore: {app_config.vectorstore.provider}")
    vectorstore = create_vectorstore(app_config, embeddings)
    
    # Step 3: Initialize (create/get collection)
    logger.info("Initializing vectorstore...")
    vectorstore.initialize()
    
    # Step 4: Add sample documents
    logger.info("Adding sample documents...")
    sample_docs = [
        "RAG stands for Retrieval-Augmented Generation, a technique for improving LLM responses.",
        "Vector databases store embeddings for efficient similarity search.",
        "ChromaDB is a popular open-source vector database for AI applications.",
        "LangChain provides abstractions for building LLM applications.",
        "Python is a great language for data science and machine learning."
    ]
    
    sample_metadata = [
        {"source": "rag_intro.txt", "topic": "RAG"},
        {"source": "vector_db.txt", "topic": "databases"},
        {"source": "chroma.txt", "topic": "databases"},
        {"source": "langchain.txt", "topic": "frameworks"},
        {"source": "python.txt", "topic": "programming"}
    ]
    
    vectorstore.add_documents(
        texts=sample_docs,
        metadatas=sample_metadata
    )
    
    # Step 5: Get stats
    stats = vectorstore.get_stats()
    logger.info(f"Vectorstore stats: {stats}")
    
    # Step 6: Query for similar documents
    logger.info("\n=== Querying ===")
    
    query = "What is RAG and how does it work?"
    logger.info(f"Query: {query}")
    
    results = vectorstore.query(query, n_results=3)
    
    logger.info(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        logger.info(f"\n--- Result {i} ---")
        logger.info(f"Text: {result['text']}")
        logger.info(f"Metadata: {result['metadata']}")
        logger.info(f"Distance: {result['distance']:.4f}")
    
    # Step 7: Query with metadata filter
    logger.info("\n=== Querying with filter ===")
    query2 = "Tell me about databases"
    logger.info(f"Query: {query2}")
    logger.info(f"Filter: topic = 'databases'")
    
    results2 = vectorstore.query(
        query2,
        n_results=2,
        where={"topic": "databases"}
    )
    
    logger.info(f"\nFound {len(results2)} results:")
    for i, result in enumerate(results2, 1):
        logger.info(f"\n--- Result {i} ---")
        logger.info(f"Text: {result['text']}")
        logger.info(f"Metadata: {result['metadata']}")
    
    logger.info("\n=== Demo Complete ===")
    logger.info("\nTo switch providers:")
    logger.info("1. Edit environment/default.toml")
    logger.info("2. Change [vectorstore] provider = 'pinecone'")
    logger.info("3. Run this script again - NO CODE CHANGES!")


if __name__ == "__main__":
    main()

