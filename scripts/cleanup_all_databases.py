#!/usr/bin/env python3
"""
Clean up all data from all vector databases.
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from trace import codes

import constants
from config import Config
from embeddings import create_embeddings
from logger import get_logger
from vectorstore import create_vectorstore

logger = get_logger(__name__)


def _cleanup_chroma(vectorstore, logger=None) -> None:
    """Clean up ChromaDB by deleting and recreating collection."""
    vectorstore.client.delete_collection(name=vectorstore.collection_name)
    vectorstore.collection = vectorstore.client.get_or_create_collection(
        name=vectorstore.collection_name,
        metadata={constants.CHROMA_HNSW_SPACE: vectorstore.distance},
    )


def _cleanup_qdrant(vectorstore, logger=None) -> None:
    """Clean up Qdrant by deleting and recreating collection."""
    vectorstore.client.delete_collection(collection_name=vectorstore.collection_name)
    from qdrant_client.models import Distance, VectorParams

    distance_map = {
        "cosine": Distance.COSINE,
        "euclidean": Distance.EUCLID,
        "dot": Distance.DOT,
    }
    vectorstore.client.create_collection(
        collection_name=vectorstore.collection_name,
        vectors_config=VectorParams(
            size=vectorstore.embeddings.dimension,
            distance=distance_map.get(vectorstore.distance, Distance.COSINE),
        ),
    )


def _cleanup_weaviate(vectorstore, logger=None) -> None:
    """Clean up Weaviate by deleting and recreating collection."""
    vectorstore.client.collections.delete(vectorstore.class_name)
    vectorstore.initialize()


def _cleanup_pinecone(vectorstore, logger) -> None:
    """Clean up Pinecone by deleting all vectors from all namespaces."""
    logger.info(
        codes.OPERATION_CLEAR, message="Retrieving all namespaces from Pinecone..."
    )

    index_stats = vectorstore.index.describe_index_stats()
    namespaces = list(index_stats.get("namespaces", {}).keys())

    logger.info(
        codes.OPERATION_CLEAR, namespaces_count=len(namespaces), namespaces=namespaces
    )

    for namespace in namespaces:
        if namespace == "":
            continue
        logger.info(
            codes.OPERATION_CLEAR,
            message=f"Deleting all vectors from namespace '{namespace}'...",
        )
        vectorstore.index.delete(delete_all=True, namespace=namespace)

    logger.info(
        codes.OPERATION_CLEAR, message="Deleting all vectors from default namespace..."
    )
    vectorstore.index.delete(delete_all=True)

    logger.info(
        codes.OPERATION_CLEAR,
        message="Waiting 3 seconds for Pinecone deletion to propagate...",
    )
    time.sleep(3)


CLEANUP_HANDLERS = {
    "chroma": _cleanup_chroma,
    "qdrant": _cleanup_qdrant,
    "weaviate": _cleanup_weaviate,
    "pinecone": _cleanup_pinecone,
}


def _cleanup_provider(provider: str, config: Config, logger) -> bool:
    """Clean up a single provider's database."""
    vectorstore = None
    try:
        logger.info(codes.OPERATION_CLEAR, provider=provider.upper())

        config.vectorstore.provider = provider

        if provider == "pinecone":
            config.vectorstore.pinecone.verify_ssl = False

        embeddings = create_embeddings(config)
        vectorstore = create_vectorstore(config, embeddings)

        vectorstore.initialize()

        stats_before = vectorstore.get_stats()
        count_before = stats_before.get(constants.STATS_KEY_COUNT, 0)
        logger.info(
            codes.VECTORSTORE_STATS, provider=provider, count_before=count_before
        )

        if count_before == 0:
            logger.info(
                codes.OPERATION_CLEAR,
                provider=provider,
                message="No documents to clean - already clean",
            )
            return True

        logger.info(codes.VECTORSTORE_DELETING, provider=provider, count=count_before)

        cleanup_handler = CLEANUP_HANDLERS.get(provider)
        if not cleanup_handler:
            logger.error(
                codes.VECTORSTORE_ERROR,
                provider=provider,
                message="No cleanup handler found",
            )
            return False

        # All cleanup handlers now accept logger parameter (uniform interface)
        cleanup_handler(vectorstore, logger)

        stats_after = vectorstore.get_stats()
        count_after = stats_after.get(constants.STATS_KEY_COUNT, 0)
        logger.info(
            codes.VECTORSTORE_DELETED,
            provider=provider,
            count_before=count_before,
            count_after=count_after,
        )
        logger.info(
            codes.OPERATION_CLEAR,
            provider=provider.upper(),
            message="Cleaned successfully",
        )
        return True

    except Exception as e:
        logger.error(
            codes.VECTORSTORE_ERROR, provider=provider, error=str(e), exc_info=True
        )
        return False
    finally:
        # Explicitly close Weaviate connections to prevent hanging
        if vectorstore and hasattr(vectorstore, "close"):
            vectorstore.close()


def main():
    """Clean up all vector databases by deleting collections."""
    providers = ["chroma", "qdrant", "weaviate", "pinecone"]

    logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
    logger.info(codes.SCRIPT_STARTED, message="CLEANING ALL VECTOR DATABASES")
    logger.info(codes.SCRIPT_STARTED, separator="=" * 70)

    results = {}
    for provider in providers:
        config = Config()
        results[provider] = _cleanup_provider(provider, config, logger)

    logger.info(codes.SCRIPT_COMPLETED, separator="=" * 70)
    logger.info(codes.SCRIPT_COMPLETED, message="CLEANUP COMPLETE FOR ALL DATABASES")
    logger.info(codes.SCRIPT_COMPLETED, separator="=" * 70)

    if all(results.values()):
        logger.info(codes.SCRIPT_EXIT_SUCCESS)
        return 0

    logger.error(codes.SCRIPT_EXIT_ERROR, message="Some cleanups failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
