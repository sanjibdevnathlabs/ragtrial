"""
Pinecone vector store implementation.

Uses Pinecone's managed vector database service.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
import uuid

from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class PineconeVectorStore:
    """
    Pinecone vector store implementation.
    
    Provides managed cloud vector storage using Pinecone with support
    for cosine, euclidean, or dotproduct similarity.
    
    Attributes:
        config: Application configuration
        embeddings: Embeddings provider for generating vectors
        index: Pinecone index instance
        index_name: Name of the Pinecone index
    """
    
    def __init__(self, config: "Config", embeddings: EmbeddingsProtocol):
        """
        Initialize Pinecone vector store.
        
        Args:
            config: Application configuration containing Pinecone settings
            embeddings: Embeddings provider for generating vectors
        """
        logger.info(codes.VECTORSTORE_INITIALIZING, provider="pinecone")
        
        # Get Pinecone-specific settings FIRST
        pinecone_config = config.vectorstore.pinecone
        
        # Configure SSL/urllib3 BEFORE importing Pinecone
        # This ensures the SSL context is set up correctly
        if not pinecone_config.verify_ssl:
            import ssl
            import urllib3
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # Set default SSL context to unverified
            ssl._create_default_https_context = ssl._create_unverified_context
            logger.warning(
                codes.VECTORSTORE_INITIALIZING,
                provider="pinecone",
                message="⚠️  SSL verification disabled - DEVELOPMENT ONLY, NOT FOR PRODUCTION"
            )
        
        # Now import Pinecone after SSL configuration
        try:
            from pinecone import Pinecone, ServerlessSpec
            self.Pinecone = Pinecone
            self.ServerlessSpec = ServerlessSpec
        except ImportError:
            error_msg = "pinecone package not installed. Run: pip install pinecone"
            logger.error(codes.VECTORSTORE_ERROR, message=error_msg)
            raise ImportError(error_msg)
        
        self.config = config
        self.embeddings = embeddings
        self.index_name = pinecone_config.index_name
        
        # Initialize Pinecone client with SSL configuration
        if pinecone_config.verify_ssl:
            # Use certifi's certificate bundle (fixes macOS SSL issues)
            import certifi
            self.pc = self.Pinecone(
                api_key=pinecone_config.api_key,
                ssl_ca_certs=certifi.where()
            )
            logger.info(
                codes.VECTORSTORE_INITIALIZING,
                provider="pinecone",
                message="Using certifi certificate bundle for SSL verification"
            )
        else:
            # Create client with SSL verification disabled
            self.pc = self.Pinecone(
                api_key=pinecone_config.api_key,
                ssl_verify=False
            )
        
        self.metric = pinecone_config.metric
        self.dimension = pinecone_config.dimension
        self.cloud = pinecone_config.cloud
        self.region = pinecone_config.region
        self.verify_ssl = pinecone_config.verify_ssl
        
        self.index = None
        
        logger.info(
            codes.VECTORSTORE_INITIALIZED,
            provider="pinecone",
            index_name=self.index_name,
            dimension=self.dimension,
            metric=self.metric,
            message=codes.MSG_VECTORSTORE_INITIALIZED
        )
    
    def initialize(self) -> None:
        """
        Initialize index - create if doesn't exist, connect if exists.
        """
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name in index_names:
                logger.info(
                    codes.VECTORSTORE_COLLECTION_EXISTS,
                    index_name=self.index_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_EXISTS
                )
            else:
                # Create index
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATING,
                    index_name=self.index_name
                )
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=self.ServerlessSpec(
                        cloud=self.cloud,
                        region=self.region
                    )
                )
                
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATED,
                    index_name=self.index_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_CREATED
                )
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="initialize",
                error=str(e),
                exc_info=True
            )
            raise
    
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
        if not self.index:
            raise RuntimeError("Index not initialized. Call initialize() first.")
        
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
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (id, embedding, text, metadata) in enumerate(zip(ids, embeddings, texts, metadatas)):
                # Add text to metadata for retrieval
                metadata_with_text = {**metadata, "text": text}
                vectors.append({
                    "id": id,
                    "values": embedding,
                    "metadata": metadata_with_text
                })
            
            # Upsert to Pinecone (batch size 100)
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(
                codes.VECTORSTORE_DOCUMENTS_ADDED,
                count=len(texts),
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
        if not self.index:
            raise RuntimeError("Index not initialized. Call initialize() first.")
        
        logger.info(
            codes.VECTORSTORE_QUERYING,
            query_text=query_text[:100],
            n_results=n_results,
            has_filter=where is not None
        )
        
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query_text)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=n_results,
                filter=where,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "text": match.metadata.get("text", ""),
                    "metadata": {k: v for k, v in match.metadata.items() if k != "text"},
                    "distance": match.score
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
        if not self.index:
            raise RuntimeError("Index not initialized. Call initialize() first.")
        
        logger.info(codes.VECTORSTORE_DELETING, count=len(ids))
        
        try:
            self.index.delete(ids=ids)
            
            logger.info(
                codes.VECTORSTORE_DELETED,
                count=len(ids)
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
            Dict with count, index_name, dimension
        """
        if not self.index:
            return {
                "index_name": self.index_name,
                "count": 0,
                "initialized": False
            }
        
        try:
            stats = self.index.describe_index_stats()
            
            result = {
                "index_name": self.index_name,
                "count": stats.total_vector_count,
                "dimension": self.dimension,
                "metric": self.metric,
                "initialized": True
            }
            
            logger.debug(codes.VECTORSTORE_STATS, **result)
            
            return result
            
        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="get_stats",
                error=str(e),
                exc_info=True
            )
            raise
    
    def clear(self) -> None:
        """
        Delete all documents from the index.
        
        Warning: This is destructive and cannot be undone!
        """
        if not self.index:
            raise RuntimeError("Index not initialized. Call initialize() first.")
        
        logger.warning(
            codes.VECTORSTORE_DELETING,
            index_name=self.index_name,
            operation="CLEAR ALL"
        )
        
        try:
            # Delete all vectors (Pinecone doesn't have a clear all command)
            self.index.delete(delete_all=True)
            
            logger.info(
                codes.VECTORSTORE_DELETED,
                index_name=self.index_name,
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

