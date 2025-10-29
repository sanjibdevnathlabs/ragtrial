#!/usr/bin/env python3
"""
Populate vector databases with sample documents.

This script adds sample documents to all configured vector databases
WITHOUT cleaning them up, so you can explore the data in the databases.
"""

import sys
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from trace import codes

import constants
from config import Config
from embeddings import create_embeddings
from logger import get_logger
from vectorstore import create_vectorstore

logger = get_logger(__name__)


def _get_sample_documents(provider: str) -> List[Dict]:
    """
    Create list of sample documents about AI and technology.

    Args:
        provider: Provider name for unique IDs

    Returns:
        List of document dictionaries
    """
    return [
        {
            "id": f"{provider}_doc_ai_overview",
            "text": "Artificial Intelligence is transforming the world through machine learning, "
            "natural language processing, and computer vision. AI systems can learn from "
            "data, recognize patterns, and make decisions with minimal human intervention.",
            "metadata": {
                "source": "AI Textbook",
                "category": "overview",
                "topic": "artificial_intelligence",
            },
        },
        {
            "id": f"{provider}_doc_ml_basics",
            "text": "Machine Learning is a subset of AI that focuses on algorithms that improve "
            "through experience. It includes supervised learning, unsupervised learning, "
            "and reinforcement learning techniques.",
            "metadata": {
                "source": "ML Guide",
                "category": "fundamentals",
                "topic": "machine_learning",
            },
        },
        {
            "id": f"{provider}_doc_nlp",
            "text": "Natural Language Processing enables computers to understand, interpret, and "
            "generate human language. Applications include chatbots, translation, "
            "sentiment analysis, and text summarization.",
            "metadata": {
                "source": "NLP Handbook",
                "category": "applications",
                "topic": "nlp",
            },
        },
        {
            "id": f"{provider}_doc_cv",
            "text": "Computer Vision allows machines to interpret and understand visual information "
            "from the world. It powers facial recognition, autonomous vehicles, medical "
            "image analysis, and augmented reality.",
            "metadata": {
                "source": "CV Research Paper",
                "category": "applications",
                "topic": "computer_vision",
            },
        },
        {
            "id": f"{provider}_doc_dl",
            "text": "Deep Learning uses neural networks with multiple layers to learn complex "
            "patterns from large amounts of data. It has achieved breakthrough results "
            "in image recognition, speech processing, and game playing.",
            "metadata": {
                "source": "DL Tutorial",
                "category": "fundamentals",
                "topic": "deep_learning",
            },
        },
        {
            "id": f"{provider}_doc_rag",
            "text": "Retrieval-Augmented Generation (RAG) combines retrieval systems with large "
            "language models to provide accurate, up-to-date responses grounded in "
            "external knowledge. RAG systems retrieve relevant documents and use them "
            "to generate contextually accurate answers.",
            "metadata": {
                "source": "RAG Paper 2024",
                "category": "advanced",
                "topic": "rag",
            },
        },
    ]


def _add_documents_to_store(vectorstore, documents: List[Dict], provider: str) -> int:
    """
    Add documents to vector store.

    Args:
        vectorstore: Vector store instance
        documents: List of documents to add
        provider: Provider name for logging

    Returns:
        Number of documents added
    """
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    ids = [doc["id"] for doc in documents]

    logger.info(
        codes.VECTORSTORE_DOCUMENTS_ADDING, provider=provider, count=len(documents)
    )

    vectorstore.add_documents(texts=texts, metadatas=metadatas, ids=ids)

    logger.info(
        codes.VECTORSTORE_DOCUMENTS_ADDED, provider=provider, count=len(documents)
    )

    return len(documents)


def _test_query(vectorstore, provider: str) -> None:
    """
    Test the vector store with a sample query.

    Args:
        vectorstore: Vector store instance
        provider: Provider name for logging
    """
    query = "What is machine learning?"

    logger.info(codes.VECTORSTORE_QUERYING, provider=provider, query=query)

    results = vectorstore.query(query_text=query, n_results=3)

    logger.info(
        codes.VECTORSTORE_QUERY_RESULTS, provider=provider, results_count=len(results)
    )

    for i, result in enumerate(results, 1):
        logger.info(
            codes.VECTORSTORE_QUERY_RESULTS,
            result_num=i,
            text=result[constants.RESULT_KEY_TEXT][:100] + "...",
            distance=result.get(constants.RESULT_KEY_DISTANCE, "N/A"),
        )


def populate_database(provider: str, config: Config) -> bool:
    """
    Populate a vector database with sample documents.

    Args:
        provider: Vector database provider name
        config: Application configuration

    Returns:
        True if successful, False otherwise
    """
    vectorstore = None
    try:
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(
            codes.SCRIPT_STARTED,
            message=f"Populating {provider.upper()} with sample data",
        )
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)

        config.vectorstore.provider = provider

        if provider == "pinecone":
            config.vectorstore.pinecone.verify_ssl = False

        embeddings = create_embeddings(config)
        vectorstore = create_vectorstore(config, embeddings)

        logger.info(codes.VECTORSTORE_INITIALIZING, provider=provider)
        vectorstore.initialize()

        sample_documents = _get_sample_documents(provider)
        _add_documents_to_store(vectorstore, sample_documents, provider)
        _test_query(vectorstore, provider)

        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(
            codes.TEST_PASSED,
            provider=provider,
            message=f"✅ {provider.upper()} POPULATED SUCCESSFULLY",
        )
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)

        return True

    except Exception as e:
        logger.error(
            codes.TEST_FAILED,
            provider=provider,
            error=str(e),
            message=f"❌ Failed to populate {provider}",
            exc_info=True,
        )
        return False
    finally:
        # Explicitly close Weaviate connections to prevent hanging
        if vectorstore and hasattr(vectorstore, "close"):
            vectorstore.close()


def main():
    """Main function to populate databases."""
    try:
        logger.info(codes.CONFIG_LOADING, message="Loading configuration...")
        config = Config()
        logger.info(codes.CONFIG_LOADED)

        providers = ["chroma", "qdrant", "weaviate", "pinecone"]
        if len(sys.argv) > 1:
            providers = [sys.argv[1].lower()]

        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(
            codes.SCRIPT_STARTED,
            message=f"Populating databases: {', '.join(providers)}",
        )
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)

        results = {}
        for provider in providers:
            logger.info(codes.SCRIPT_STARTED, separator="")
            success = populate_database(provider, config)
            results[provider] = success
            logger.info(codes.SCRIPT_STARTED, separator="")

        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(codes.SCRIPT_STARTED, message="POPULATION SUMMARY")
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)

        for provider, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(codes.SCRIPT_STARTED, message=f"{provider.upper()}: {status}")

        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)

        if not all(results.values()):
            logger.error(codes.SCRIPT_EXIT_ERROR)
            return 1

        logger.info(codes.SCRIPT_EXIT_SUCCESS)
        return 0

    except Exception as e:
        logger.error(codes.SCRIPT_EXIT_ERROR, error=str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
