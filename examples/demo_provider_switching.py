"""
Demonstration of provider switching - ORM-like flexibility.

This script shows how you can switch between different vectorstore
and embeddings providers by ONLY changing the config file.

The application code remains EXACTLY the same!

Supported Embeddings Providers:
- Google (text-embedding-004)
- OpenAI (text-embedding-3-small/large)
- HuggingFace (sentence-transformers)
- Cohere (embed-english-v3.0)
- Anthropic (Voyage AI - voyage-2)

Supported Vectorstore Providers:
- ChromaDB (local persistent storage)
- Pinecone (managed cloud service)
- Qdrant (open-source vector search)
- Weaviate (cloud-native vector database)

To switch providers:
1. Edit environment/default.toml
2. Change [embeddings] provider = "..."
3. Change [vectorstore] provider = "..."
4. Run this script - NO CODE CHANGES!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from trace import codes

import constants
from config import Config
from embeddings import create_embeddings
from logger import get_logger, setup_logging
from vectorstore import create_vectorstore

logger = get_logger(__name__)

try:
    app_config = Config()
except FileNotFoundError as e:
    logger.error(
        codes.CONFIG_LOAD_FAILED, error=str(e), message=constants.CONFIG_FILE_NOT_FOUND
    )
    sys.exit(1)

setup_logging(app_config.logging, app_config.app)


def _display_configuration():
    """Display current provider configuration."""
    logger.info(codes.CONFIG_LOADED, separator="=" * 60)
    logger.info(codes.DEMO_STARTED, message="PROVIDER SWITCHING DEMONSTRATION")
    logger.info(codes.CONFIG_LOADED, separator="=" * 60)

    logger.info(codes.CONFIG_LOADED, section="Current Configuration:")
    logger.info(
        codes.CONFIG_LOADED,
        embeddings_provider=app_config.embeddings.provider,
        vectorstore_provider=app_config.vectorstore.provider,
        embedding_dimension=app_config.embeddings.dimension,
    )


def _create_embeddings_provider():
    """Create and initialize embeddings provider."""
    logger.info(codes.EMBEDDINGS_CREATING, message="Creating embeddings provider...")

    try:
        embeddings = create_embeddings(app_config)
        logger.info(
            codes.EMBEDDINGS_INITIALIZED,
            provider=app_config.embeddings.provider.upper(),
            message="Embeddings initialized",
        )
        return embeddings
    except Exception as e:
        logger.error(
            codes.EMBEDDINGS_ERROR,
            provider=app_config.embeddings.provider,
            error=str(e),
            exc_info=True,
        )
        logger.info(codes.DEMO_INSTRUCTIONS, message="Make sure you have:")
        logger.info(
            codes.DEMO_INSTRUCTIONS,
            step=f"1. Installed package for {app_config.embeddings.provider}",
        )
        logger.info(
            codes.DEMO_INSTRUCTIONS, step="2. Set the appropriate API key (if required)"
        )
        sys.exit(1)


def _create_vectorstore_provider(embeddings):
    """Create and initialize vectorstore provider."""
    logger.info(codes.VECTORSTORE_CREATING, message="Creating vectorstore...")

    try:
        vectorstore = create_vectorstore(app_config, embeddings)
        logger.info(
            codes.VECTORSTORE_INITIALIZED,
            provider=app_config.vectorstore.provider.upper(),
            message="Vectorstore initialized",
        )
        return vectorstore
    except Exception as e:
        logger.error(
            codes.VECTORSTORE_ERROR,
            provider=app_config.vectorstore.provider,
            error=str(e),
            exc_info=True,
        )
        logger.info(codes.DEMO_INSTRUCTIONS, message="Make sure you have:")
        logger.info(
            codes.DEMO_INSTRUCTIONS,
            step=f"1. Installed package for {app_config.vectorstore.provider}",
        )
        logger.info(
            codes.DEMO_INSTRUCTIONS, step="2. Service is running (if self-hosted)"
        )
        logger.info(
            codes.DEMO_INSTRUCTIONS, step="3. API key is configured (if cloud service)"
        )
        sys.exit(1)


def _get_sample_documents():
    """Get sample documents for demonstration."""
    return [
        "Retrieval-Augmented Generation (RAG) combines retrieval with generation for better LLM responses.",
        "Vector databases enable efficient similarity search for AI applications.",
        f"{app_config.vectorstore.provider.title()} is a powerful vector database solution.",
        f"{app_config.embeddings.provider.title()} provides high-quality embeddings for text.",
        "The ORM-like abstraction allows switching providers with just config changes.",
    ]


def _get_sample_metadata():
    """Get sample metadata for demonstration."""
    return [
        {"topic": "RAG", "category": "concepts"},
        {"topic": "databases", "category": "infrastructure"},
        {"topic": "databases", "category": "providers"},
        {"topic": "embeddings", "category": "providers"},
        {"topic": "architecture", "category": "design"},
    ]


def _add_sample_data(vectorstore):
    """Add sample documents to vectorstore."""
    logger.info(
        codes.VECTORSTORE_DOCUMENTS_ADDING, message="Adding sample documents..."
    )

    sample_docs = _get_sample_documents()
    sample_metadata = _get_sample_metadata()

    try:
        vectorstore.add_documents(texts=sample_docs, metadatas=sample_metadata)
        logger.info(codes.VECTORSTORE_DOCUMENTS_ADDED, count=len(sample_docs))
    except Exception as e:
        logger.error(codes.VECTORSTORE_ERROR, error=str(e), exc_info=True)
        sys.exit(1)


def _test_query(vectorstore):
    """Test vectorstore with sample query."""
    logger.info(codes.VECTORSTORE_QUERYING, message="Querying vectorstore...")

    query = "How does the architecture support provider switching?"

    try:
        results = vectorstore.query(query, n_results=3)
        logger.info(codes.VECTORSTORE_QUERY_RESULTS, results_count=len(results))
        logger.info(codes.VECTORSTORE_QUERY_RESULTS, query=query)

        for i, result in enumerate(results, 1):
            logger.info(
                codes.VECTORSTORE_QUERY_RESULTS,
                result_num=i,
                text=result[constants.RESULT_KEY_TEXT][:100] + "...",
                category=result[constants.RESULT_KEY_METADATA].get("category", "N/A"),
                distance=f"{result[constants.RESULT_KEY_DISTANCE]:.4f}",
            )
    except Exception as e:
        logger.error(codes.VECTORSTORE_ERROR, error=str(e), exc_info=True)
        sys.exit(1)


def _display_statistics(vectorstore):
    """Display vectorstore statistics."""
    logger.info(codes.VECTORSTORE_STATS, message="Vectorstore Statistics:")
    stats = vectorstore.get_stats()
    for key, value in stats.items():
        logger.info(codes.VECTORSTORE_STATS, stat_key=key, stat_value=value)


def _display_summary():
    """Display demonstration summary."""
    logger.info(codes.DEMO_COMPLETED, separator="=" * 60)
    logger.info(codes.DEMO_COMPLETED, message="✅ DEMONSTRATION COMPLETE")
    logger.info(codes.DEMO_COMPLETED, separator="=" * 60)

    logger.info(codes.DEMO_INSTRUCTIONS, message="To switch providers:")
    logger.info(codes.DEMO_INSTRUCTIONS, step="1. Edit environment/default.toml")
    logger.info(
        codes.DEMO_INSTRUCTIONS,
        step="2. Change [embeddings] provider = 'openai' (or other)",
    )
    logger.info(
        codes.DEMO_INSTRUCTIONS,
        step="3. Change [vectorstore] provider = 'pinecone' (or other)",
    )
    logger.info(
        codes.DEMO_INSTRUCTIONS, step="4. Rerun this script - NO CODE CHANGES NEEDED!"
    )

    logger.info(
        codes.DEMO_INSTRUCTIONS, message="The same application code works with:"
    )
    logger.info(
        codes.DEMO_INSTRUCTIONS,
        providers="Embeddings: google, openai, huggingface, cohere, anthropic",
    )
    logger.info(
        codes.DEMO_INSTRUCTIONS,
        providers="Vectorstores: chroma, pinecone, qdrant, weaviate",
    )


def main():
    """Demonstrate provider-agnostic usage."""
    _display_configuration()

    embeddings = _create_embeddings_provider()
    vectorstore = _create_vectorstore_provider(embeddings)

    logger.info(codes.VECTORSTORE_INITIALIZING, message="Initializing collection...")
    vectorstore.initialize()

    _add_sample_data(vectorstore)
    _test_query(vectorstore)
    _display_statistics(vectorstore)
    _display_summary()


if __name__ == "__main__":
    main()
