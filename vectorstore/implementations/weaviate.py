"""
Weaviate vector store implementation.

Uses Weaviate's cloud-native vector database.
"""

import json
import uuid
from trace import codes
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import constants
from embeddings.base import EmbeddingsProtocol
from logger import get_logger

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
            from weaviate.classes.config import (
                Configure,
                DataType,
                Property,
                VectorDistances,
            )
            from weaviate.config import AdditionalConfig, Timeout

            self.weaviate = weaviate
            self.Configure = Configure
            self.VectorDistances = VectorDistances
            self.Property = Property
            self.DataType = DataType
            self.Timeout = Timeout
            self.AdditionalConfig = AdditionalConfig
        except ImportError:
            logger.error(
                codes.VECTORSTORE_ERROR, message=constants.ERROR_WEAVIATE_NOT_INSTALLED
            )
            raise ImportError(constants.ERROR_WEAVIATE_NOT_INSTALLED)

        self.config = config
        self.embeddings = embeddings

        # Get Weaviate-specific settings
        weaviate_config = config.vectorstore.weaviate
        self.class_name = weaviate_config.class_name

        distance_map = {
            "cosine": self.VectorDistances.COSINE,
            "l2-squared": self.VectorDistances.L2_SQUARED,
            "dot": self.VectorDistances.DOT,
            "hamming": self.VectorDistances.HAMMING,
            "manhattan": self.VectorDistances.MANHATTAN,
        }

        has_api_key = weaviate_config.api_key and weaviate_config.api_key.strip()

        if not has_api_key:
            url_clean = weaviate_config.url.replace(
                constants.URL_HTTP_PREFIX, ""
            ).replace(constants.URL_HTTPS_PREFIX, "")

            if constants.URL_COLON not in url_clean:
                host = url_clean
                port = weaviate_config.default_http_port

                self.client = self.weaviate.connect_to_local(
                    host=host,
                    port=port,
                    additional_config=self.AdditionalConfig(
                        timeout=self.Timeout(query=30, insert=60, init=10)
                    ),
                )

                self.distance = distance_map.get(
                    weaviate_config.distance.lower(), self.VectorDistances.COSINE
                )
                self.collection = None

                logger.info(
                    codes.VECTORSTORE_INITIALIZED,
                    provider="weaviate",
                    class_name=self.class_name,
                    message=codes.MSG_VECTORSTORE_INITIALIZED,
                )
                return

            host, port_str = url_clean.split(constants.URL_COLON, 1)
            port = int(port_str)

            self.client = self.weaviate.connect_to_local(
                host=host,
                port=port,
                additional_config=self.AdditionalConfig(
                    timeout=self.Timeout(query=30, insert=60, init=10)
                ),
            )

            self.distance = distance_map.get(
                weaviate_config.distance.lower(), self.VectorDistances.COSINE
            )
            self.collection = None

            logger.info(
                codes.VECTORSTORE_INITIALIZED,
                provider="weaviate",
                class_name=self.class_name,
                message=codes.MSG_VECTORSTORE_INITIALIZED,
            )
            return

        url_parts = weaviate_config.url.replace(constants.URL_HTTP_PREFIX, "").replace(
            constants.URL_HTTPS_PREFIX, ""
        )
        is_secure = constants.URL_HTTPS in weaviate_config.url

        if constants.URL_COLON not in url_parts:
            host = url_parts
            http_port = (
                weaviate_config.default_https_port
                if is_secure
                else weaviate_config.default_http_port
            )

            self.client = self.weaviate.connect_to_custom(
                http_host=host,
                http_port=http_port,
                http_secure=is_secure,
                grpc_host=host,
                grpc_port=weaviate_config.grpc_port,
                grpc_secure=is_secure,
                auth_credentials=self.weaviate.auth.AuthApiKey(weaviate_config.api_key),
                additional_config=self.AdditionalConfig(
                    timeout=self.Timeout(query=30, insert=60, init=10)
                ),
            )

            self.distance = distance_map.get(
                weaviate_config.distance.lower(), self.VectorDistances.COSINE
            )
            self.collection = None

            logger.info(
                codes.VECTORSTORE_INITIALIZED,
                provider="weaviate",
                class_name=self.class_name,
                message=codes.MSG_VECTORSTORE_INITIALIZED,
            )
            return

        host, port = url_parts.split(constants.URL_COLON, 1)
        http_port = int(port)

        self.client = self.weaviate.connect_to_custom(
            http_host=host,
            http_port=http_port,
            http_secure=is_secure,
            grpc_host=host,
            grpc_port=weaviate_config.grpc_port,
            grpc_secure=is_secure,
            auth_credentials=self.weaviate.auth.AuthApiKey(weaviate_config.api_key),
            additional_config=self.AdditionalConfig(
                timeout=self.Timeout(query=30, insert=60, init=10)
            ),
        )

        self.distance = distance_map.get(
            weaviate_config.distance.lower(), self.VectorDistances.COSINE
        )
        self.collection = None

        logger.info(
            codes.VECTORSTORE_INITIALIZED,
            provider="weaviate",
            class_name=self.class_name,
            url=weaviate_config.url,
            message=codes.MSG_VECTORSTORE_INITIALIZED,
        )

    def initialize(self) -> None:
        """
        Initialize class - create if doesn't exist, get if exists.
        """
        try:
            if not self.client.collections.exists(self.class_name):
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATING, class_name=self.class_name
                )

                self.embeddings.get_dimension()

                self.collection = self.client.collections.create(
                    name=self.class_name,
                    vector_config=self.Configure.Vectors.self_provided(
                        vector_index_config=self.Configure.VectorIndex.hnsw(
                            distance_metric=self.distance
                        )
                    ),
                    properties=[
                        self.Property(
                            name=constants.WEAVIATE_PROPERTY_TEXT,
                            data_type=self.DataType.TEXT,
                        ),
                        self.Property(
                            name=constants.WEAVIATE_PROPERTY_METADATA,
                            data_type=self.DataType.TEXT,
                        ),
                    ],
                )

                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATED,
                    class_name=self.class_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_CREATED,
                )
                return

            logger.info(
                codes.VECTORSTORE_COLLECTION_EXISTS,
                class_name=self.class_name,
                message=codes.MSG_VECTORSTORE_COLLECTION_EXISTS,
            )
            self.collection = self.client.collections.get(self.class_name)

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation=constants.OPERATION_INITIALIZE,
                error=str(e),
                exc_info=True,
            )
            raise

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            texts: List of document text strings
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        logger.info(codes.VECTORSTORE_DOCUMENTS_ADDING, count=len(texts))

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        # Generate default metadata if not provided
        if metadatas is None:
            metadatas = [{} for _ in range(len(texts))]

        try:
            # Generate embeddings for documents
            embeddings = self.embeddings.embed_documents(texts)

            # Use fixed batch instead of dynamic to prevent hanging
            from weaviate.classes.data import DataObject

            objects_to_insert = []
            for id, embedding, text, metadata in zip(ids, embeddings, texts, metadatas):
                uuid_obj = (
                    uuid.uuid5(uuid.NAMESPACE_DNS, id) if isinstance(id, str) else id
                )
                objects_to_insert.append(
                    DataObject(
                        properties={
                            constants.WEAVIATE_PROPERTY_TEXT: text,
                            constants.WEAVIATE_PROPERTY_METADATA: json.dumps(metadata),
                        },
                        vector=embedding,
                        uuid=uuid_obj,
                    )
                )

            # Insert in smaller batches of 10
            batch_size = 10
            for i in range(0, len(objects_to_insert), batch_size):
                batch = objects_to_insert[i : i + batch_size]
                self.collection.data.insert_many(batch)

            logger.info(
                codes.VECTORSTORE_DOCUMENTS_ADDED,
                count=len(texts),
                message=codes.MSG_VECTORSTORE_DOCUMENTS_ADDED,
            )

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation=constants.OPERATION_ADD_DOCUMENTS,
                error=str(e),
                exc_info=True,
            )
            raise

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
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
            has_filter=where is not None,
        )

        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query_text)

            # Query Weaviate
            response = self.collection.query.near_vector(
                near_vector=query_embedding,
                limit=n_results,
                return_metadata=["distance"],
            )

            # Format results
            formatted_results = []
            for obj in response.objects:
                metadata_str = obj.properties.get(
                    constants.WEAVIATE_PROPERTY_METADATA, "{}"
                )
                try:
                    metadata = (
                        json.loads(metadata_str)
                        if isinstance(metadata_str, str)
                        else metadata_str
                    )
                except json.JSONDecodeError:
                    metadata = {}

                formatted_results.append(
                    {
                        constants.RESULT_KEY_ID: str(obj.uuid),
                        constants.RESULT_KEY_TEXT: obj.properties.get(
                            constants.WEAVIATE_PROPERTY_TEXT, ""
                        ),
                        constants.RESULT_KEY_METADATA: metadata,
                        constants.RESULT_KEY_DISTANCE: (
                            obj.metadata.distance
                            if hasattr(obj.metadata, "distance")
                            else 0.0
                        ),
                    }
                )

            logger.info(codes.VECTORSTORE_QUERY_RESULTS, count=len(formatted_results))

            return formatted_results

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation=constants.OPERATION_QUERY,
                error=str(e),
                exc_info=True,
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
                uuid_obj = (
                    uuid.uuid5(uuid.NAMESPACE_DNS, id) if isinstance(id, str) else id
                )
                self.collection.data.delete_by_id(uuid_obj)

            logger.info(codes.VECTORSTORE_DELETED, count=len(ids))

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation=constants.OPERATION_DELETE,
                error=str(e),
                exc_info=True,
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
                "initialized": True,
            }

            logger.debug(codes.VECTORSTORE_STATS, **stats)

            return stats

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation=constants.OPERATION_GET_STATS,
                error=str(e),
                exc_info=True,
            )
            return {"class_name": self.class_name, "count": 0, "initialized": False}

    def clear(self) -> None:
        """
        Delete all documents from the class.

        Warning: This is destructive and cannot be undone!
        """
        logger.warning(
            codes.VECTORSTORE_DELETING,
            class_name=self.class_name,
            operation="CLEAR ALL",
        )

        try:
            # Delete class and recreate it
            self.client.collections.delete(self.class_name)

            # Reinitialize
            self.initialize()

            logger.info(
                codes.VECTORSTORE_DELETED,
                class_name=self.class_name,
                operation="CLEAR ALL",
            )

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation=constants.OPERATION_CLEAR,
                error=str(e),
                exc_info=True,
            )
            raise

    def check_health(self) -> bool:
        """
        Fast health check using Weaviate API.

        Returns:
            True if Weaviate is responsive, False otherwise
        """
        logger.debug(codes.HEALTH_CHECK_VECTORSTORE_CHECKING, provider="weaviate")

        try:
            # Check if client is ready
            if not self.client or not self.client.is_ready():
                return False

            logger.debug(codes.HEALTH_CHECK_VECTORSTORE_HEALTHY, provider="weaviate")
            return True

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_VECTORSTORE_UNHEALTHY,
                provider="weaviate",
                error=str(e),
                exc_info=True,
            )
            return False

    def close(self):
        """Explicitly close the Weaviate client connection."""
        if hasattr(self, "client") and self.client:
            try:
                self.client.close()
                logger.debug("Weaviate client connection closed")
            except Exception as e:
                logger.warning(f"Error closing Weaviate client: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.close()
        return False

    def __del__(self):
        """Close Weaviate client on cleanup."""
        self.close()
