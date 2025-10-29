"""
Qdrant vector store implementation.

Uses Qdrant's open-source vector search engine.
"""

import uuid
from trace import codes
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import constants
from embeddings.base import EmbeddingsProtocol
from logger import get_logger

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
            from qdrant_client.models import Distance, PointStruct, VectorParams

            self.QdrantClient = QdrantClient
            self.Distance = Distance
            self.VectorParams = VectorParams
            self.PointStruct = PointStruct
        except ImportError:
            logger.error(
                codes.VECTORSTORE_ERROR, message=constants.ERROR_QDRANT_NOT_INSTALLED
            )
            raise ImportError(constants.ERROR_QDRANT_NOT_INSTALLED)

        self.config = config
        self.embeddings = embeddings
        self.collection_name = config.vectorstore.collection_name

        # Get Qdrant-specific settings
        qdrant_config = config.vectorstore.qdrant

        has_api_key = qdrant_config.api_key and qdrant_config.api_key.strip()

        if not has_api_key:
            self.client = self.QdrantClient(
                host=qdrant_config.host,
                port=qdrant_config.port,
                prefer_grpc=qdrant_config.prefer_grpc,
            )
            self.distance = qdrant_config.distance
            self.vector_size = qdrant_config.vector_size

            logger.info(
                codes.VECTORSTORE_INITIALIZED,
                provider="qdrant",
                collection_name=self.collection_name,
                message=codes.MSG_VECTORSTORE_INITIALIZED,
            )
            return

        self.client = self.QdrantClient(
            url=f"http://{qdrant_config.host}:{qdrant_config.port}",
            api_key=qdrant_config.api_key,
            prefer_grpc=qdrant_config.prefer_grpc,
        )

        # Map distance function
        distance_map = {
            "cosine": self.Distance.COSINE,
            "euclid": self.Distance.EUCLID,
            "dot": self.Distance.DOT,
        }
        self.distance = distance_map.get(
            qdrant_config.distance.lower(), self.Distance.COSINE
        )

        logger.info(
            codes.VECTORSTORE_INITIALIZED,
            provider="qdrant",
            collection_name=self.collection_name,
            host=qdrant_config.host,
            port=qdrant_config.port,
            message=codes.MSG_VECTORSTORE_INITIALIZED,
        )

    def initialize(self) -> None:
        """
        Initialize collection - create if doesn't exist, get if exists.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.collection_name not in collection_names:
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATING,
                    collection_name=self.collection_name,
                )

                dimension = self.embeddings.get_dimension()

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=self.VectorParams(
                        size=dimension, distance=self.distance
                    ),
                )

                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATED,
                    collection_name=self.collection_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_CREATED,
                )

            if self.collection_name in collection_names:
                logger.info(
                    codes.VECTORSTORE_COLLECTION_EXISTS,
                    collection_name=self.collection_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_EXISTS,
                )

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

        ids = ids or [str(uuid.uuid4()) for _ in range(len(texts))]
        metadatas = metadatas or [{} for _ in range(len(texts))]

        try:
            embeddings = self.embeddings.embed_documents(texts)

            points = []
            for id, embedding, text, metadata in zip(ids, embeddings, texts, metadatas):
                payload = {**metadata, constants.QDRANT_PAYLOAD_TEXT: text}
                id_uuid = (
                    str(uuid.uuid5(uuid.NAMESPACE_DNS, id))
                    if isinstance(id, str)
                    else id
                )
                points.append(
                    self.PointStruct(id=id_uuid, vector=embedding, payload=payload)
                )

            self.client.upsert(collection_name=self.collection_name, points=points)

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
            where: Optional metadata filter (Qdrant filter format)

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
            query_embedding = self.embeddings.embed_query(query_text)

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=n_results,
                query_filter=where,
            )

            formatted_results = []
            for hit in results:
                payload = hit.payload or {}
                text = payload.pop(constants.QDRANT_PAYLOAD_TEXT, "")
                formatted_results.append(
                    {
                        constants.RESULT_KEY_ID: str(hit.id),
                        constants.RESULT_KEY_TEXT: text,
                        constants.RESULT_KEY_METADATA: payload,
                        constants.RESULT_KEY_DISTANCE: hit.score,
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
            uuid_ids = [
                str(uuid.uuid5(uuid.NAMESPACE_DNS, id)) if isinstance(id, str) else id
                for id in ids
            ]

            self.client.delete(
                collection_name=self.collection_name, points_selector=uuid_ids
            )

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
            Dict with count, collection_name
        """
        try:
            info = self.client.get_collection(self.collection_name)

            stats = {
                constants.STATS_KEY_COLLECTION_NAME: self.collection_name,
                constants.STATS_KEY_COUNT: info.points_count,
                constants.STATS_KEY_VECTORS_COUNT: info.vectors_count,
                constants.STATS_KEY_INDEXED_VECTORS_COUNT: info.indexed_vectors_count,
                constants.STATS_KEY_INITIALIZED: True,
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
            return {
                constants.STATS_KEY_COLLECTION_NAME: self.collection_name,
                constants.STATS_KEY_COUNT: 0,
                constants.STATS_KEY_INITIALIZED: False,
            }

    def clear(self) -> None:
        """
        Delete all documents from the collection.

        Warning: This is destructive and cannot be undone!
        """
        logger.warning(
            codes.VECTORSTORE_DELETING,
            collection_name=self.collection_name,
            operation=constants.OPERATION_CLEAR_ALL,
        )

        try:
            self.client.delete_collection(self.collection_name)

            dimension = self.embeddings.get_dimension()
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.VectorParams(
                    size=dimension, distance=self.distance
                ),
            )

            logger.info(
                codes.VECTORSTORE_DELETED,
                collection_name=self.collection_name,
                operation=constants.OPERATION_CLEAR_ALL,
            )

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation=constants.OPERATION_CLEAR,
                error=str(e),
                exc_info=True,
            )
            raise
