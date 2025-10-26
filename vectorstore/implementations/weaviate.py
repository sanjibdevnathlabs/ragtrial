"""
Weaviate vector store implementation.

Uses Weaviate's cloud-native vector database.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
import json
import uuid

from embeddings.base import EmbeddingsProtocol
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class WeaviateVectorStore:
    """
    Weaviate vector store implementation.
    
    Provides vector storage using Weaviate (self-hosted or cloud) with
    support for cosine, L2, dot product, and other distance metrics.
    
    Attributes:
        config: Application configuration
        embeddings: Embeddings provider for generating vectors
        client: Weaviate client instance
        class_name: Name of the Weaviate class (collection)
    """
    
    def __init__(self, config: "Config", embeddings: EmbeddingsProtocol):
        """
        Initialize Weaviate vector store.
        
        Args:
            config: Application configuration containing Weaviate settings
            embeddings: Embeddings provider for generating vectors
        """
        logger.info(codes.VECTORSTORE_INITIALIZING, provider="weaviate")
        
        try:
            import weaviate
            from weaviate.classes.config import Configure, VectorDistances, Property, DataType
            self.weaviate = weaviate
            self.Configure = Configure
            self.VectorDistances = VectorDistances
            self.Property = Property
            self.DataType = DataType
        except ImportError:
            error_msg = "weaviate-client package not installed. Run: pip install weaviate-client"
            logger.error(codes.VECTORSTORE_ERROR, message=error_msg)
            raise ImportError(error_msg)
        
        self.config = config
        self.embeddings = embeddings
        
        # Get Weaviate-specific settings
        weaviate_config = config.vectorstore.weaviate
        self.class_name = weaviate_config.class_name
        
        # Initialize Weaviate client
        # Check if API key is set and not empty
        has_api_key = weaviate_config.api_key and weaviate_config.api_key.strip()
        
        if has_api_key:
            # Cloud or authenticated instance
            # Extract host and port from URL
            url_parts = weaviate_config.url.replace("http://", "").replace("https://", "")
            if ":" in url_parts:
                host, port = url_parts.split(":", 1)
                http_port = int(port)
            else:
                host = url_parts
                # Use configured default ports based on protocol
                is_secure = "https" in weaviate_config.url
                http_port = weaviate_config.default_https_port if is_secure else weaviate_config.default_http_port
            
            # Use different ports for HTTP and gRPC (cannot be the same on same host)
            is_secure = "https" in weaviate_config.url
            self.client = self.weaviate.connect_to_custom(
                http_host=host,
                http_port=http_port,
                http_secure=is_secure,
                grpc_host=host,
                grpc_port=weaviate_config.grpc_port,
                grpc_secure=is_secure,
                auth_credentials=self.weaviate.auth.AuthApiKey(weaviate_config.api_key)
            )
        else:
            # Local instance without authentication
            # Extract host and port from URL
            url_clean = weaviate_config.url.replace("http://", "").replace("https://", "")
            if ":" in url_clean:
                host, port_str = url_clean.split(":", 1)
                port = int(port_str)
            else:
                host = url_clean
                # Use configured default HTTP port
                port = weaviate_config.default_http_port
            
            self.client = self.weaviate.connect_to_local(
                host=host,
                port=port
            )
        
        # Map distance function
        distance_map = {
            "cosine": self.VectorDistances.COSINE,
            "l2-squared": self.VectorDistances.L2_SQUARED,
            "dot": self.VectorDistances.DOT,
            "hamming": self.VectorDistances.HAMMING,
            "manhattan": self.VectorDistances.MANHATTAN
        }
        self.distance = distance_map.get(
            weaviate_config.distance.lower(),
            self.VectorDistances.COSINE
        )
        
        logger.info(
            codes.VECTORSTORE_INITIALIZED,
            provider="weaviate",
            class_name=self.class_name,
            url=weaviate_config.url,
            message=codes.MSG_VECTORSTORE_INITIALIZED
        )
    
    def initialize(self) -> None:
        """
        Initialize class - create if doesn't exist, get if exists.
        """
        try:
            # Check if class exists
            if self.client.collections.exists(self.class_name):
                logger.info(
                    codes.VECTORSTORE_COLLECTION_EXISTS,
                    class_name=self.class_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_EXISTS
                )
                # Get existing collection
                self.collection = self.client.collections.get(self.class_name)
            else:
                # Create class
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATING,
                    class_name=self.class_name
                )
                
                # Get dimension from embeddings
                dimension = self.embeddings.get_dimension()
                
                # Use Weaviate v4 API with proper Property classes
                # Note: Store metadata as TEXT (JSON string) instead of OBJECT
                # because OBJECT requires nested property definitions
                self.collection = self.client.collections.create(
                    name=self.class_name,
                    vectorizer_config=self.Configure.Vectorizer.none(),
                    vector_index_config=self.Configure.VectorIndex.hnsw(
                        distance_metric=self.distance
                    ),
                    properties=[
                        self.Property(
                            name="text",
                            data_type=self.DataType.TEXT
                        ),
                        self.Property(
                            name="metadata",
                            data_type=self.DataType.TEXT  # Store as JSON string
                        )
                    ]
                )
                
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATED,
                    class_name=self.class_name,
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
            
            # Prepare objects for Weaviate
            with self.collection.batch.dynamic() as batch:
                for id, embedding, text, metadata in zip(ids, embeddings, texts, metadatas):
                    # Weaviate requires UUID format, convert string IDs to UUID
                    if isinstance(id, str):
                        # Generate deterministic UUID from string ID
                        uuid_obj = uuid.uuid5(uuid.NAMESPACE_DNS, id)
                    else:
                        uuid_obj = id
                    
                    batch.add_object(
                        properties={
                            "text": text,
                            "metadata": json.dumps(metadata)  # Serialize metadata as JSON string
                        },
                        vector=embedding,
                        uuid=uuid_obj
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
            where: Optional metadata filter (Weaviate filter format)
            
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
            
            # Query Weaviate
            response = self.collection.query.near_vector(
                near_vector=query_embedding,
                limit=n_results,
                return_metadata=["distance"]
            )
            
            # Format results
            formatted_results = []
            for obj in response.objects:
                # Deserialize metadata from JSON string back to dict
                metadata_str = obj.properties.get("metadata", "{}")
                try:
                    metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                except json.JSONDecodeError:
                    metadata = {}
                
                formatted_results.append({
                    "id": str(obj.uuid),
                    "text": obj.properties.get("text", ""),
                    "metadata": metadata,
                    "distance": obj.metadata.distance if hasattr(obj.metadata, 'distance') else 0.0
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
            for id in ids:
                # Convert string ID to UUID (same as in add_documents)
                if isinstance(id, str):
                    uuid_obj = uuid.uuid5(uuid.NAMESPACE_DNS, id)
                else:
                    uuid_obj = id
                
                self.collection.data.delete_by_id(uuid_obj)
            
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
            Dict with count, class_name
        """
        try:
            # Get aggregate count
            result = self.collection.aggregate.over_all(total_count=True)
            
            stats = {
                "class_name": self.class_name,
                "count": result.total_count,
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
                "class_name": self.class_name,
                "count": 0,
                "initialized": False
            }
    
    def clear(self) -> None:
        """
        Delete all documents from the class.
        
        Warning: This is destructive and cannot be undone!
        """
        logger.warning(
            codes.VECTORSTORE_DELETING,
            class_name=self.class_name,
            operation="CLEAR ALL"
        )
        
        try:
            # Delete class and recreate it
            self.client.collections.delete(self.class_name)
            
            # Reinitialize
            self.initialize()
            
            logger.info(
                codes.VECTORSTORE_DELETED,
                class_name=self.class_name,
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
    
    def __del__(self):
        """Close Weaviate client on cleanup."""
        if hasattr(self, 'client'):
            self.client.close()

