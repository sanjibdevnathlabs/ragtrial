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
    """Demonstrate provider-agnostic usage."""
    
    logger.info("=" * 60)
    logger.info("PROVIDER SWITCHING DEMONSTRATION")
    logger.info("=" * 60)
    
    # Show current configuration
    logger.info(f"\n📊 Current Configuration:")
    logger.info(f"   Embeddings Provider: {app_config.embeddings.provider}")
    logger.info(f"   Vectorstore Provider: {app_config.vectorstore.provider}")
    logger.info(f"   Embedding Dimension: {app_config.embeddings.dimension}")
    
    # Step 1: Create embeddings provider
    logger.info(f"\n🔧 Creating embeddings provider...")
    try:
        embeddings = create_embeddings(app_config)
        logger.info(f"   ✅ {app_config.embeddings.provider.upper()} embeddings initialized")
    except Exception as e:
        logger.error(f"   ❌ Failed to initialize embeddings: {e}")
        logger.info("\n💡 Make sure you have:")
        logger.info(f"   1. Installed the required package for {app_config.embeddings.provider}")
        logger.info("   2. Set the appropriate API key (if required)")
        sys.exit(1)
    
    # Step 2: Create vectorstore
    logger.info(f"\n🔧 Creating vectorstore...")
    try:
        vectorstore = create_vectorstore(app_config, embeddings)
        logger.info(f"   ✅ {app_config.vectorstore.provider.upper()} vectorstore initialized")
    except Exception as e:
        logger.error(f"   ❌ Failed to initialize vectorstore: {e}")
        logger.info("\n💡 Make sure you have:")
        logger.info(f"   1. Installed the required package for {app_config.vectorstore.provider}")
        logger.info("   2. Service is running (if self-hosted)")
        logger.info("   3. API key is configured (if cloud service)")
        sys.exit(1)
    
    # Step 3: Initialize collection
    logger.info(f"\n🔧 Initializing collection...")
    vectorstore.initialize()
    
    # Step 4: Test with sample data
    logger.info(f"\n📝 Adding sample documents...")
    sample_docs = [
        "Retrieval-Augmented Generation (RAG) combines retrieval with generation for better LLM responses.",
        "Vector databases enable efficient similarity search for AI applications.",
        f"{app_config.vectorstore.provider.title()} is a powerful vector database solution.",
        f"{app_config.embeddings.provider.title()} provides high-quality embeddings for text.",
        "The ORM-like abstraction allows switching providers with just config changes."
    ]
    
    sample_metadata = [
        {"topic": "RAG", "category": "concepts"},
        {"topic": "databases", "category": "infrastructure"},
        {"topic": "databases", "category": "providers"},
        {"topic": "embeddings", "category": "providers"},
        {"topic": "architecture", "category": "design"}
    ]
    
    try:
        vectorstore.add_documents(
            texts=sample_docs,
            metadatas=sample_metadata
        )
        logger.info(f"   ✅ Added {len(sample_docs)} documents")
    except Exception as e:
        logger.error(f"   ❌ Failed to add documents: {e}")
        sys.exit(1)
    
    # Step 5: Query
    logger.info(f"\n🔍 Querying vectorstore...")
    query = "How does the architecture support provider switching?"
    
    try:
        results = vectorstore.query(query, n_results=3)
        logger.info(f"   ✅ Found {len(results)} results")
        
        logger.info(f"\n📊 Query Results for: '{query}'")
        for i, result in enumerate(results, 1):
            logger.info(f"\n   Result {i}:")
            logger.info(f"   Text: {result['text'][:100]}...")
            logger.info(f"   Category: {result['metadata'].get('category', 'N/A')}")
            logger.info(f"   Distance: {result['distance']:.4f}")
    except Exception as e:
        logger.error(f"   ❌ Query failed: {e}")
        sys.exit(1)
    
    # Step 6: Statistics
    logger.info(f"\n📈 Vectorstore Statistics:")
    stats = vectorstore.get_stats()
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("✅ DEMONSTRATION COMPLETE")
    logger.info("=" * 60)
    logger.info("\n💡 To switch providers:")
    logger.info("   1. Edit environment/default.toml")
    logger.info("   2. Change [embeddings] provider = 'openai' (or other)")
    logger.info("   3. Change [vectorstore] provider = 'pinecone' (or other)")
    logger.info("   4. Rerun this script - NO CODE CHANGES NEEDED!")
    logger.info("\n🎯 The same application code works with:")
    logger.info("   Embeddings: google, openai, huggingface, cohere, anthropic")
    logger.info("   Vectorstores: chroma, pinecone, qdrant, weaviate")


if __name__ == "__main__":
    main()

