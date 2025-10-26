#!/usr/bin/env python3
"""
Populate vector databases with sample documents.

This script adds sample documents to all configured vector databases
WITHOUT cleaning them up, so you can explore the data in the databases.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config
from embeddings import create_embeddings
from vectorstore import create_vectorstore
from logger import get_logger
from trace import codes

logger = get_logger(__name__)


def populate_database(provider: str, config: Config):
    """
    Populate a vector database with sample documents.
    
    Args:
        provider: Vector database provider name
        config: Application configuration
    """
    try:
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(
            codes.SCRIPT_STARTED, 
            message=f"Populating {provider.upper()} with sample data"
        )
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        
        # Set provider
        config.vectorstore.provider = provider
        
        # Force SSL off for Pinecone (dev environment)
        if provider == 'pinecone':
            config.vectorstore.pinecone.verify_ssl = False
        
        # Create embeddings and vectorstore
        embeddings = create_embeddings(config)
        vectorstore = create_vectorstore(config, embeddings)
        
        # Initialize
        logger.info(codes.VECTORSTORE_INITIALIZING, provider=provider)
        vectorstore.initialize()
        
        # Sample documents about AI and technology
        sample_documents = [
            {
                "id": f"{provider}_doc_ai_overview",
                "text": "Artificial Intelligence is transforming the world through machine learning, "
                       "natural language processing, and computer vision. AI systems can learn from "
                       "data, recognize patterns, and make decisions with minimal human intervention.",
                "metadata": {
                    "source": "AI Textbook",
                    "category": "overview",
                    "topic": "artificial_intelligence"
                }
            },
            {
                "id": f"{provider}_doc_ml_basics",
                "text": "Machine Learning is a subset of AI that focuses on algorithms that improve "
                       "through experience. It includes supervised learning, unsupervised learning, "
                       "and reinforcement learning techniques.",
                "metadata": {
                    "source": "ML Guide",
                    "category": "fundamentals",
                    "topic": "machine_learning"
                }
            },
            {
                "id": f"{provider}_doc_nlp",
                "text": "Natural Language Processing enables computers to understand, interpret, and "
                       "generate human language. Applications include chatbots, translation, "
                       "sentiment analysis, and text summarization.",
                "metadata": {
                    "source": "NLP Handbook",
                    "category": "applications",
                    "topic": "nlp"
                }
            },
            {
                "id": f"{provider}_doc_cv",
                "text": "Computer Vision allows machines to interpret and understand visual information "
                       "from the world. It powers facial recognition, autonomous vehicles, medical "
                       "image analysis, and augmented reality.",
                "metadata": {
                    "source": "CV Research Paper",
                    "category": "applications",
                    "topic": "computer_vision"
                }
            },
            {
                "id": f"{provider}_doc_dl",
                "text": "Deep Learning uses neural networks with multiple layers to learn complex "
                       "patterns from large amounts of data. It has achieved breakthrough results "
                       "in image recognition, speech processing, and game playing.",
                "metadata": {
                    "source": "DL Tutorial",
                    "category": "fundamentals",
                    "topic": "deep_learning"
                }
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
                    "topic": "rag"
                }
            },
            {
                "id": f"{provider}_doc_embeddings",
                "text": "Vector embeddings represent text, images, or other data as dense numerical "
                       "vectors in high-dimensional space. Similar items have similar embeddings, "
                       "enabling semantic search and similarity matching.",
                "metadata": {
                    "source": "Embeddings Guide",
                    "category": "fundamentals",
                    "topic": "embeddings"
                }
            },
            {
                "id": f"{provider}_doc_vectordb",
                "text": "Vector databases store and efficiently search high-dimensional vector embeddings. "
                       "They enable fast semantic search, recommendation systems, and similarity "
                       "matching at scale using algorithms like HNSW and IVF.",
                "metadata": {
                    "source": "VectorDB Overview",
                    "category": "infrastructure",
                    "topic": "vector_databases"
                }
            }
        ]
        
        # Add documents
        logger.info(
            codes.VECTORSTORE_DOCUMENTS_ADDING,
            count=len(sample_documents),
            message=f"Adding {len(sample_documents)} sample documents to {provider}..."
        )
        
        # Extract texts, metadatas, and ids from sample documents
        texts = [doc["text"] for doc in sample_documents]
        metadatas = [doc["metadata"] for doc in sample_documents]
        ids = [doc["id"] for doc in sample_documents]
        
        vectorstore.add_documents(texts=texts, metadatas=metadatas, ids=ids)
        
        logger.info(
            codes.VECTORSTORE_DOCUMENTS_ADDED,
            count=len(sample_documents),
            provider=provider,
            message=f"✅ Successfully added {len(sample_documents)} documents to {provider}"
        )
        
        # Get stats
        stats = vectorstore.get_stats()
        logger.info(
            codes.VECTORSTORE_STATS,
            provider=provider,
            stats=stats,
            message=f"Database stats: {stats}"
        )
        
        # Test query
        logger.info(codes.SCRIPT_STARTED, separator="-" * 70)
        logger.info(codes.VECTORSTORE_QUERYING, message="Testing query...")
        
        test_query = "What is RAG and how does it work?"
        results = vectorstore.query(test_query, n_results=2)
        
        logger.info(
            codes.VECTORSTORE_QUERY_RESULTS,
            count=len(results),
            message=f"Query returned {len(results)} result(s)"
        )
        
        for i, result in enumerate(results, 1):
            logger.info(
                codes.VECTORSTORE_QUERY_RESULTS,
                result_num=i,
                text=result["text"][:100] + "...",
                distance=result.get("distance", "N/A")
            )
        
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(
            codes.TEST_PASSED,
            provider=provider,
            message=f"✅ {provider.upper()} POPULATED SUCCESSFULLY"
        )
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(
            codes.TEST_FAILED,
            provider=provider,
            error=str(e),
            message=f"❌ Failed to populate {provider}"
        )
        import traceback
        logger.error(codes.TEST_FAILED, traceback=traceback.format_exc())
        return False


def main():
    """Main function to populate databases."""
    try:
        # Load config
        logger.info(codes.CONFIG_LOADING, message="Loading configuration...")
        config = Config()
        logger.info(codes.CONFIG_LOADED)
        
        # Get provider from command line or use all
        if len(sys.argv) > 1:
            providers = [sys.argv[1].lower()]
        else:
            # Populate all providers
            providers = ["chroma", "qdrant", "weaviate", "pinecone"]
        
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(
            codes.SCRIPT_STARTED,
            message=f"Populating databases: {', '.join(providers)}"
        )
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        
        results = {}
        for provider in providers:
            logger.info(codes.SCRIPT_STARTED, separator="")
            success = populate_database(provider, config)
            results[provider] = success
            logger.info(codes.SCRIPT_STARTED, separator="")
        
        # Summary
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        logger.info(codes.SCRIPT_STARTED, message="POPULATION SUMMARY")
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        
        for provider, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(codes.SCRIPT_STARTED, message=f"{provider.upper()}: {status}")
        
        logger.info(codes.SCRIPT_STARTED, separator="=" * 70)
        
        # Return exit code
        if all(results.values()):
            logger.info(codes.SCRIPT_EXIT_SUCCESS)
            return 0
        else:
            logger.error(codes.SCRIPT_EXIT_ERROR)
            return 1
            
    except Exception as e:
        logger.error(codes.SCRIPT_EXIT_ERROR, error=str(e))
        import traceback
        logger.error(codes.SCRIPT_EXIT_ERROR, traceback=traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())

