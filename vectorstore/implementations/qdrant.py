"""
Qdrant vector store implementation.

Uses Qdrant's open-source vector search engine.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
import uuid

from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class QdrantVectorStore:
    """
    Qdrant vector store implementation.
    
    Provides vector storage using Qdrant (self-hosted or cloud) with
    support for Cosine, Euclidean, or Dot product similarity.
    
    Attributes:
        config: Application configuration
        embeddings: Embeddings provider for generating vectors
        client: Qdrant client instance
        collection_name: Name of the Qdrant collection
    """
    
    def __init__(self, config: "Config", embeddings: EmbeddingsProtocol):
        """
        Initialize Qdrant vector store.
        
        Args:
            config: Application configuration containing Qdrant settings
            embeddings: Embeddings provider for generating vectors
        """
        logger.info(codes.VECTORSTORE_INITIALIZING, provider="qdrant")
        
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct
            self.QdrantClient = QdrantClient
            self.Distance = Distance
            self.VectorParams = VectorParams
            self.PointStruct = PointStruct
        except ImportError:
            error_msg = "qdrant-client package not installed. Run: pip install qdrant-client"
            logger.error(codes.VECTORSTORE_ERROR, message=error_msg)
            raise ImportError(error_msg)
        
        self.config = config
        self.embeddings = embeddings
        self.collection_name = config.vectorstore.collection_name
        
        # Get Qdrant-specific settings
        qdrant_config = config.vectorstore.qdrant
        
        # Initialize Qdrant client
        # Check if API key is set and not empty
        has_api_key = qdrant_config.api_key and qdrant_config.api_key.strip()
        
        if has_api_key:
            # Cloud or authenticated instance
            self.client = self.QdrantClient(
                url=f"http://{qdrant_config.host}:{qdrant_config.port}",
                api_key=qdrant_config.api_key,
                prefer_grpc=qdrant_config.prefer_grpc
            )
        else:
            # Local instance without authentication
            self.client = self.QdrantClient(
                host=qdrant_config.host,
                port=qdrant_config.port,
                prefer_grpc=qdrant_config.prefer_grpc
            )
        
        # Map distance function
        distance_map = {
            "cosine": self.Distance.COSINE,
            "euclid": self.Distance.EUCLID,
            "dot": self.Distance.DOT
        }
        self.distance = distance_map.get(
            qdrant_config.distance.lower(),
            self.Distance.COSINE
        )
        
        logger.info(
            codes.VECTORSTORE_INITIALIZED,
            provider="qdrant",
            collection_name=self.collection_name,
            host=qdrant_config.host,
            port=qdrant_config.port,
            message=codes.MSG_VECTORSTORE_INITIALIZED
        )
    
    def initialize(self) -> None:
        """
        Initialize collection - create if doesn't exist, get if exists.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name in collection_names:
                logger.info(
                    codes.VECTORSTORE_COLLECTION_EXISTS,
                    collection_name=self.collection_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_EXISTS
                )
            else:
                # Create collection
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATING,
                    collection_name=self.collection_name
                )
                
                # Get dimension from embeddings
                dimension = self.embeddings.get_dimension()
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=self.VectorParams(
                        size=dimension,
                        distance=self.distance
                    )
                )
                
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATED,
                    collection_name=self.collection_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_CREATED
                )
            
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
            
            # Prepare points for Qdrant
            points = []
            for id, embedding, text, metadata in zip(ids, embeddings, texts, metadatas):
                # Add text to payload for retrieval
                payload = {**metadata, "text": text}
                # Qdrant requires UUID or integer IDs, convert string IDs to UUID
                if isinstance(id, str):
                    # Generate UUID from string ID for consistency
                    id_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, id))
                else:
                    id_uuid = id
                points.append(
                    self.PointStruct(
                        id=id_uuid,
                        vector=embedding,
                        payload=payload
                    )
                )
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
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
            where: Optional metadata filter (Qdrant filter format)
            
        Returns:
            List of result dicts with id, text, metadata, distance
        """
        logger.info(
            codes.VECTORSTORE_QUERYING,
            query_text=query_text[:100],
            n_results=n_results,
            has_filter=where is not None
        )
        
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query_text)
            
            # Query Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=n_results,
                query_filter=where
            )
            
            # Format results
            formatted_results = []
            for hit in results:
                payload = hit.payload or {}
                text = payload.pop("text", "")
                formatted_results.append({
                    "id": str(hit.id),
                    "text": text,
                    "metadata": payload,
                    "distance": hit.score
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
        logger.info(codes.VECTORSTORE_DELETING, count=len(ids))
        
        try:
            # Convert string IDs to UUIDs (same as in add_documents)
            uuid_ids = []
            for id in ids:
                if isinstance(id, str):
                    uuid_ids.append(str(uuid.uuid5(uuid.NAMESPACE_DNS, id)))
                else:
                    uuid_ids.append(id)
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=uuid_ids
            )
            
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
            Dict with count, collection_name
        """
        try:
            info = self.client.get_collection(self.collection_name)
            
            stats = {
                "collection_name": self.collection_name,
                "count": info.points_count,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "initialized": True
            }
            
            logger.debug(codes.VECTORSTORE_STATS, **stats)
            
            return stats
            
        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="get_stats",
                error=str(e),
                exc_info=True
            )
            return {
                "collection_name": self.collection_name,
                "count": 0,
                "initialized": False
            }
    
    def clear(self) -> None:
        """
        Delete all documents from the collection.
        
        Warning: This is destructive and cannot be undone!
        """
        logger.warning(
            codes.VECTORSTORE_DELETING,
            collection_name=self.collection_name,
            operation="CLEAR ALL"
        )
        
        try:
            # Delete collection and recreate it
            self.client.delete_collection(self.collection_name)
            
            # Recreate collection
            dimension = self.embeddings.get_dimension()
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.VectorParams(
                    size=dimension,
                    distance=self.distance
                )
            )
            
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

