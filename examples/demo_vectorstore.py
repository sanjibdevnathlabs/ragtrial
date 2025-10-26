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

sys.path.insert(0, str(Path(__file__).parent.parent))

import constants
from config import Config
from embeddings import create_embeddings
from logger import get_logger, setup_logging
from trace import codes
from vectorstore import create_vectorstore

logger = get_logger(__name__)

try:
    app_config = Config()
except FileNotFoundError as e:
    logger.error(codes.CONFIG_LOAD_FAILED, error=str(e), message=constants.CONFIG_FILE_NOT_FOUND)
    sys.exit(1)

setup_logging(app_config.logging, app_config.app)


def _get_sample_documents():
    """Return sample documents for demo."""
    return [
        "RAG stands for Retrieval-Augmented Generation, a technique for improving LLM responses.",
        "Vector databases store embeddings for efficient similarity search.",
        "ChromaDB is a popular open-source vector database for AI applications.",
        "LangChain provides abstractions for building LLM applications.",
        "Python is a great language for data science and machine learning."
    ]


def _get_sample_metadata():
    """Return sample metadata for demo."""
    return [
        {"source": "rag_intro.txt", "topic": "RAG"},
        {"source": "vector_db.txt", "topic": "databases"},
        {"source": "chroma.txt", "topic": "databases"},
        {"source": "langchain.txt", "topic": "frameworks"},
        {"source": "python.txt", "topic": "programming"}
    ]


def _demonstrate_basic_query(vectorstore):
    """Demonstrate basic similarity search."""
    logger.info(codes.DEMO_QUERY_STARTED, separator="=== Querying ===")
    
    query = "What is RAG and how does it work?"
    logger.info(codes.VECTORSTORE_QUERYING, query=query)
    
    results = vectorstore.query(query, n_results=3)
    
    logger.info(codes.VECTORSTORE_QUERY_RESULTS, results_count=len(results))
    for i, result in enumerate(results, 1):
        logger.info(
            codes.VECTORSTORE_QUERY_RESULTS,
            result_num=i,
            text=result[constants.RESULT_KEY_TEXT],
            metadata=result[constants.RESULT_KEY_METADATA],
            distance=f"{result[constants.RESULT_KEY_DISTANCE]:.4f}"
        )


def _demonstrate_filtered_query(vectorstore):
    """Demonstrate metadata filtered search."""
    logger.info(codes.DEMO_QUERY_STARTED, separator="=== Querying with filter ===")
    
    query = "Tell me about databases"
    filter_topic = "databases"
    
    logger.info(codes.VECTORSTORE_QUERYING, query=query, filter=f"topic = '{filter_topic}'")
    
    results = vectorstore.query(
        query,
        n_results=2,
        where={"topic": filter_topic}
    )
    
    logger.info(codes.VECTORSTORE_QUERY_RESULTS, results_count=len(results))
    for i, result in enumerate(results, 1):
        logger.info(
            codes.VECTORSTORE_QUERY_RESULTS,
            result_num=i,
            text=result[constants.RESULT_KEY_TEXT],
            metadata=result[constants.RESULT_KEY_METADATA]
        )


def main():
    """Demonstrate vectorstore usage."""
    logger.info(codes.DEMO_STARTED, separator="=== Vectorstore Demo ===")
    
    logger.info(codes.EMBEDDINGS_CREATING, provider=app_config.embeddings.provider)
    embeddings = create_embeddings(app_config)
    
    logger.info(codes.VECTORSTORE_CREATING, provider=app_config.vectorstore.provider)
    vectorstore = create_vectorstore(app_config, embeddings)
    
    logger.info(codes.VECTORSTORE_INITIALIZING)
    vectorstore.initialize()
    
    logger.info(codes.VECTORSTORE_DOCUMENTS_ADDING)
    vectorstore.add_documents(
        texts=_get_sample_documents(),
        metadatas=_get_sample_metadata()
    )
    
    stats = vectorstore.get_stats()
    logger.info(codes.VECTORSTORE_STATS, stats=stats)
    
    _demonstrate_basic_query(vectorstore)
    _demonstrate_filtered_query(vectorstore)
    
    logger.info(codes.DEMO_COMPLETED, separator="=== Demo Complete ===")
    logger.info(codes.DEMO_INSTRUCTIONS, message="To switch providers:")
    logger.info(codes.DEMO_INSTRUCTIONS, step="1. Edit environment/default.toml")
    logger.info(codes.DEMO_INSTRUCTIONS, step="2. Change [vectorstore] provider = 'pinecone'")
    logger.info(codes.DEMO_INSTRUCTIONS, step="3. Run this script again - NO CODE CHANGES!")


if __name__ == "__main__":
    main()
