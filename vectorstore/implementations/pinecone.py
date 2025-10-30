"""
Pinecone vector store implementation.

Uses Pinecone's managed vector database service.
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
                message=constants.MSG_SSL_DISABLED_PINECONE_DEV,
            )

        # Now import Pinecone after SSL configuration
        try:
            from pinecone import Pinecone, ServerlessSpec

            self.Pinecone = Pinecone
            self.ServerlessSpec = ServerlessSpec
        except ImportError:
            logger.error(
                codes.VECTORSTORE_ERROR, message=constants.ERROR_PINECONE_NOT_INSTALLED
            )
            raise ImportError(constants.ERROR_PINECONE_NOT_INSTALLED)

        self.config = config
        self.embeddings = embeddings
        self.index_name = pinecone_config.index_name

        # Initialize Pinecone client with SSL configuration
        if not pinecone_config.verify_ssl:
            self.pc = self.Pinecone(api_key=pinecone_config.api_key, ssl_verify=False)

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
                message=codes.MSG_VECTORSTORE_INITIALIZED,
            )
            return

        # Use certifi's certificate bundle (fixes macOS SSL issues)
        import certifi

        self.pc = self.Pinecone(
            api_key=pinecone_config.api_key, ssl_ca_certs=certifi.where()
        )
        logger.info(
            codes.VECTORSTORE_INITIALIZING,
            provider="pinecone",
            message=constants.MSG_SSL_CERTIFI_BUNDLE,
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
            message=codes.MSG_VECTORSTORE_INITIALIZED,
        )

    def initialize(self) -> None:
        """
        Initialize index - create if doesn't exist, connect if exists.
        """
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]

            if self.index_name not in index_names:
                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATING, index_name=self.index_name
                )

                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=self.ServerlessSpec(cloud=self.cloud, region=self.region),
                )

                logger.info(
                    codes.VECTORSTORE_COLLECTION_CREATED,
                    index_name=self.index_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_CREATED,
                )

            if self.index_name in index_names:
                logger.info(
                    codes.VECTORSTORE_COLLECTION_EXISTS,
                    index_name=self.index_name,
                    message=codes.MSG_VECTORSTORE_COLLECTION_EXISTS,
                )

            # Connect to index
            self.index = self.pc.Index(self.index_name)

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
        if not self.index:
            raise RuntimeError(constants.ERROR_INDEX_NOT_INITIALIZED)

        logger.info(codes.VECTORSTORE_DOCUMENTS_ADDING, count=len(texts))

        ids = ids or [str(uuid.uuid4()) for _ in range(len(texts))]
        metadatas = metadatas or [{} for _ in range(len(texts))]

        self._upsert_documents(texts, metadatas, ids)

    def _upsert_documents(
        self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]
    ) -> None:
        """
        Generate embeddings and upsert documents to Pinecone.

        Args:
            texts: List of document text strings
            metadatas: List of metadata dicts
            ids: List of document IDs
        """
        try:
            embeddings = self.embeddings.embed_documents(texts)
            vectors = self._prepare_vectors(ids, embeddings, texts, metadatas)
            self._batch_upsert(vectors)

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

    def _prepare_vectors(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        texts: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Prepare vectors for Pinecone upsert.

        Args:
            ids: List of document IDs
            embeddings: List of embedding vectors
            texts: List of document texts
            metadatas: List of metadata dicts

        Returns:
            List of vector dicts for Pinecone
        """
        vectors = []
        for id, embedding, text, metadata in zip(ids, embeddings, texts, metadatas):
            metadata_with_text = {**metadata, constants.PINECONE_METADATA_TEXT: text}
            vectors.append(
                {
                    constants.PINECONE_VECTOR_ID: id,
                    constants.PINECONE_VECTOR_VALUES: embedding,
                    constants.PINECONE_VECTOR_METADATA: metadata_with_text,
                }
            )
        return vectors

    def _batch_upsert(self, vectors: List[Dict[str, Any]]) -> None:
        """
        Upsert vectors to Pinecone in batches of 100.

        Args:
            vectors: List of vector dicts to upsert
        """
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch)

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
            where: Optional metadata filter

        Returns:
            List of result dicts with id, text, metadata, distance
        """
        if not self.index:
            raise RuntimeError(constants.ERROR_INDEX_NOT_INITIALIZED)

        logger.info(
            codes.VECTORSTORE_QUERYING,
            query_text=query_text[:100],
            n_results=n_results,
            has_filter=where is not None,
        )

        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query_text)

            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=n_results,
                filter=where,
                include_metadata=True,
            )

            formatted_results = []
            for match in results.matches:
                formatted_results.append(
                    {
                        constants.RESULT_KEY_ID: match.id,
                        constants.RESULT_KEY_TEXT: match.metadata.get(
                            constants.PINECONE_METADATA_TEXT, ""
                        ),
                        constants.RESULT_KEY_METADATA: {
                            k: v
                            for k, v in match.metadata.items()
                            if k != constants.PINECONE_METADATA_TEXT
                        },
                        constants.RESULT_KEY_DISTANCE: match.score,
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
        if not self.index:
            raise RuntimeError(constants.ERROR_INDEX_NOT_INITIALIZED)

        logger.info(codes.VECTORSTORE_DELETING, count=len(ids))

        try:
            self.index.delete(ids=ids)

            logger.info(codes.VECTORSTORE_DELETED, count=len(ids))

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR, operation="delete", error=str(e), exc_info=True
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
                constants.STATS_KEY_INDEX_NAME: self.index_name,
                constants.STATS_KEY_COUNT: 0,
                constants.STATS_KEY_INITIALIZED: False,
            }

        try:
            stats = self.index.describe_index_stats()

            result = {
                constants.STATS_KEY_INDEX_NAME: self.index_name,
                constants.STATS_KEY_COUNT: stats.total_vector_count,
                constants.STATS_KEY_DIMENSION: self.dimension,
                constants.STATS_KEY_METRIC: self.metric,
                constants.STATS_KEY_INITIALIZED: True,
            }

            logger.debug(codes.VECTORSTORE_STATS, **result)

            return result

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR,
                operation="get_stats",
                error=str(e),
                exc_info=True,
            )
            raise

    def clear(self) -> None:
        """
        Delete all documents from the index.

        Warning: This is destructive and cannot be undone!
        """
        if not self.index:
            raise RuntimeError(constants.ERROR_INDEX_NOT_INITIALIZED)

        logger.warning(
            codes.VECTORSTORE_DELETING,
            index_name=self.index_name,
            operation="CLEAR ALL",
        )

        try:
            # Delete all vectors (Pinecone doesn't have a clear all command)
            self.index.delete(delete_all=True)

            logger.info(
                codes.VECTORSTORE_DELETED,
                index_name=self.index_name,
                operation="CLEAR ALL",
            )

        except Exception as e:
            logger.error(
                codes.VECTORSTORE_ERROR, operation="clear", error=str(e), exc_info=True
            )
            raise

    def check_health(self) -> bool:
        """
        Fast health check using Pinecone API.

        Returns:
            True if Pinecone is responsive, False otherwise
        """
        logger.debug(codes.HEALTH_CHECK_VECTORSTORE_CHECKING, provider="pinecone")

        try:
            # Use describe_index_stats as a lightweight health check
            if not self.index:
                return False

            self.index.describe_index_stats()

            logger.debug(codes.HEALTH_CHECK_VECTORSTORE_HEALTHY, provider="pinecone")
            return True

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_VECTORSTORE_UNHEALTHY,
                provider="pinecone",
                error=str(e),
                exc_info=True,
            )
            return False
