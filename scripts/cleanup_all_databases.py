#!/usr/bin/env python3
"""
Clean up all data from all vector databases.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config
from embeddings import create_embeddings
from vectorstore import create_vectorstore
from logger import get_logger
from trace import codes
import constants

logger = get_logger(__name__)


def main():
    """Clean up all vector databases by deleting collections."""
    providers = ['chroma', 'qdrant', 'weaviate', 'pinecone']
    
    print("=" * 70)
    print("🧹 CLEANING ALL VECTOR DATABASES")
    print("=" * 70)
    
    for provider in providers:
        try:
            print(f"\n📦 Cleaning {provider.upper()}...")
            
            # Load config and set provider
            config = Config()
            config.vectorstore.provider = provider
            
            # Force SSL off for Pinecone (dev environment)
            if provider == 'pinecone':
                config.vectorstore.pinecone.verify_ssl = False
            
            # Create embeddings and vectorstore
            embeddings = create_embeddings(config)
            vectorstore = create_vectorstore(config, embeddings)
            
            # Initialize the vectorstore to ensure collection exists
            vectorstore.initialize()
            
            # Get stats before deletion
            stats_before = vectorstore.get_stats()
            count_before = stats_before.get('count', 0)
            print(f"  Before: {count_before} documents")
            
            if count_before == 0:
                print(f"  ℹ️  No documents to clean")
                print(f"  ✅ {provider.upper()} is already clean!")
                continue
            
            # Delete the entire collection (implementation-specific)
            logger.info(
                codes.VECTORSTORE_DELETING,
                provider=provider,
                count=count_before
            )
            
            # Call the provider-specific cleanup method
            # Note: Pinecone uses 'index' attribute, not 'client'
            if hasattr(vectorstore, 'client') or hasattr(vectorstore, 'index'):
                if provider == 'chroma':
                    # Delete and recreate collection in ChromaDB
                    vectorstore.client.delete_collection(name=vectorstore.collection_name)
                    vectorstore.collection = vectorstore.client.get_or_create_collection(
                        name=vectorstore.collection_name,
                        metadata={"hnsw:space": vectorstore.distance}
                    )
                elif provider == 'qdrant':
                    # Delete and recreate collection in Qdrant
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
                            distance=distance_map.get(vectorstore.distance, Distance.COSINE)
                        )
                    )
                elif provider == 'weaviate':
                    # Delete and recreate collection in Weaviate
                    vectorstore.client.collections.delete(vectorstore.class_name)
                    # Reinitialize will recreate it
                    vectorstore.initialize()
                elif provider == 'pinecone':
                    # Delete all vectors from all namespaces in Pinecone index
                    print(f"  📋 Retrieving all namespaces from Pinecone...")
                    
                    # Get index statistics to find all namespaces
                    index_stats = vectorstore.index.describe_index_stats()
                    namespaces = list(index_stats.get('namespaces', {}).keys())
                    
                    print(f"  📁 Found {len(namespaces)} namespace(s): {namespaces if namespaces else 'None'}")
                    
                    # Delete vectors from each named namespace (skip empty string = default)
                    for namespace in namespaces:
                        if namespace == '':
                            # Empty string means default namespace, skip it here
                            continue
                        print(f"  🗑️  Deleting all vectors from namespace '{namespace}'...")
                        vectorstore.index.delete(delete_all=True, namespace=namespace)
                    
                    # Delete from the default namespace (no namespace parameter)
                    print(f"  🗑️  Deleting all vectors from default namespace...")
                    vectorstore.index.delete(delete_all=True)
                    
                    # Wait for eventual consistency
                    print(f"  ⏳ Waiting 3 seconds for Pinecone deletion to propagate...")
                    time.sleep(3)
            
            # Get stats after deletion
            stats_after = vectorstore.get_stats()
            count_after = stats_after.get('count', 0)
            print(f"  After: {count_after} documents")
            print(f"  ✅ {provider.upper()} cleaned successfully!")
            
        except Exception as e:
            print(f"  ❌ Failed to clean {provider}: {str(e)}")
            logger.error(
                codes.VECTORSTORE_ERROR,
                provider=provider,
                error=str(e)
            )
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE FOR ALL DATABASES!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())

