"""
ChromaDB vector store implementation.

Uses ChromaDB for local persistent vector storage with cosine/L2/IP similarity.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import uuid

import chromadb
from chromadb.config import Settings

from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class ChromaVectorStore:
    """
    ChromaDB vector store implementation.
    
    Provides persistent local vector storage using ChromaDB with support
    for cosine, L2, or inner product distance functions.
    
    Attributes:
        config: Application configuration
        embeddings: Embeddings provider for generating vectors
        client: ChromaDB client instance
        collection: ChromaDB collection for storing vectors
    """
    
    def __init__(self, config: "Config", embeddings: EmbeddingsProtocol):
        """
        Initialize ChromaDB vector store.
        
        Args:
            config: Application configuration containing ChromaDB settings
            embeddings: Embeddings provider for generating vectors
        """
        logger.info(codes.VECTORSTORE_INITIALIZING, provider="chroma")
        
        self.config = config
        self.embeddings = embeddings
        self.collection_name = config.vectorstore.collection_name
        
        # Get ChromaDB-specific settings
        chroma_config = config.vectorstore.chroma
        self.persist_directory = chroma_config.persist_directory
        self.distance_function = chroma_config.distance_function
        
        # Create persist directory if it doesn't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(
            Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=chroma_config.anonymized_telemetry
            )
        )
        
        self.collection = None
        
        logger.info(
            codes.VECTORSTORE_INITIALIZED,
            provider="chroma",
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
            distance=self.distance_function,
            message=codes.MSG_VECTORSTORE_INITIALIZED
        )
    
    def initialize(self) -> None:
        """
        Initialize collection - create if doesn't exist, get if exists.
        """
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(
                name=self.collection_name
            )
            
            logger.info(
                codes.VECTORSTORE_COLLECTION_EXISTS,
                collection_name=self.collection_name,
                count=self.collection.count(),
                message=codes.MSG_VECTORSTORE_COLLECTION_EXISTS
            )
            
        except Exception:
            # Collection doesn't exist, create it
            logger.info(
                codes.VECTORSTORE_COLLECTION_CREATING,
                collection_name=self.collection_name
            )
            
            # Map distance function to ChromaDB format
            distance_map = {
                "cosine": "cosine",
                "l2": "l2",
                "ip": "ip"
            }
            
            metadata = {
                "hnsw:space": distance_map.get(
                    self.distance_function.lower(),
                    "cosine"
                )
            }
            
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata=metadata
            )
            
            logger.info(
                codes.VECTORSTORE_COLLECTION_CREATED,
                collection_name=self.collection_name,
                message=codes.MSG_VECTORSTORE_COLLECTION_CREATED
            )
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document text strings
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize() first.")
        
        logger.info(
            codes.VECTORSTORE_DOCUMENTS_ADDING,
            count=len(texts)
        )
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Generate default metadata if not provided
        if metadatas is None:
            metadatas = [{} for _ in range(len(texts))]
        
        try:
            # Generate embeddings for documents
            embeddings = self.embeddings.embed_documents(texts)
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(
                codes.VECTORSTORE_DOCUMENTS_ADDED,
                count=len(texts),
                total_count=self.collection.count(),
                message=codes.MSG_VECTORSTORE_DOCUMENTS_ADDED
            )
            
        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="add_documents",
                error=str(e),
                exc_info=True
            )
            raise
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of result dicts with id, text, metadata, distance
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize() first.")
        
        logger.info(
            codes.VECTORSTORE_QUERYING,
            query_text=query_text[:100],  # Log first 100 chars
            n_results=n_results,
            has_filter=where is not None
        )
        
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query_text)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            logger.info(
                codes.VECTORSTORE_QUERY_RESULTS,
                count=len(formatted_results)
            )
            
            return formatted_results
            
        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="query",
                error=str(e),
                exc_info=True
            )
            raise
    
    def delete(self, ids: List[str]) -> None:
        """
        Delete documents from the vector store.
        
        Args:
            ids: List of document IDs to delete
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize() first.")
        
        logger.info(codes.VECTORSTORE_DELETING, count=len(ids))
        
        try:
            self.collection.delete(ids=ids)
            
            logger.info(
                codes.VECTORSTORE_DELETED,
                count=len(ids),
                remaining=self.collection.count()
            )
            
        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="delete",
                error=str(e),
                exc_info=True
            )
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dict with count, collection_name, persist_directory
        """
        if not self.collection:
            return {
                "collection_name": self.collection_name,
                "count": 0,
                "initialized": False
            }
        
        stats = {
            "collection_name": self.collection_name,
            "count": self.collection.count(),
            "persist_directory": self.persist_directory,
            "distance_function": self.distance_function,
            "initialized": True
        }
        
        logger.debug(codes.VECTORSTORE_STATS, **stats)
        
        return stats
    
    def clear(self) -> None:
        """
        Delete all documents from the collection.
        
        Warning: This is destructive and cannot be undone!
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize() first.")
        
        logger.warning(
            codes.VECTORSTORE_DELETING,
            collection_name=self.collection_name,
            count=self.collection.count(),
            operation="CLEAR ALL"
        )
        
        try:
            # Get all IDs and delete them
            all_data = self.collection.get()
            if all_data["ids"]:
                self.collection.delete(ids=all_data["ids"])
            
            logger.info(
                codes.VECTORSTORE_DELETED,
                collection_name=self.collection_name,
                operation="CLEAR ALL"
            )
            
        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="clear",
                error=str(e),
                exc_info=True
            )
            raise

