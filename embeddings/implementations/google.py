"""
Google embeddings implementation using Google Generative AI.

Uses Google's text-embedding-004 model for generating embeddings.
"""

from trace import codes
from typing import TYPE_CHECKING, List

import google.generativeai as genai

import constants
from logger import get_logger

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class GoogleEmbeddings:
    """
    Google embeddings provider implementation.

    Uses Google's Generative AI API for creating embeddings with
    the text-embedding-004 model.

    Attributes:
        config: Application configuration
        model: Model name (e.g., "models/text-embedding-004")
        task_type: Task type for embeddings ("retrieval_document" or "retrieval_query")
        batch_size: Number of texts to process in one batch
        dimension: Embedding dimension
    """

    def __init__(self, config: "Config"):
        """
        Initialize Google embeddings provider.

        Args:
            config: Application configuration containing Google API settings
        """
        logger.info(codes.EMBEDDINGS_INITIALIZING, provider="google")

        self.config = config
        self.model = config.embeddings.google.model
        self.task_type = config.embeddings.google.task_type
        self.batch_size = config.embeddings.google.batch_size
        self.title = config.embeddings.google.title
        self.dimension = config.embeddings.dimension

        # Configure Google API (should already be done, but ensure it's set)
        if config.google.api_key:
            genai.configure(api_key=config.google.api_key)

        logger.info(
            codes.EMBEDDINGS_INITIALIZED,
            provider="google",
            model=self.model,
            dimension=self.dimension,
            message=codes.MSG_EMBEDDINGS_INITIALIZED,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Processes texts in batches to respect API limits and improve performance.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        logger.info(
            codes.EMBEDDINGS_GENERATING, count=len(texts), batch_size=self.batch_size
        )

        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_num = i // self.batch_size + 1

            batch_embeddings = self._process_batch(batch, batch_num)
            all_embeddings.extend(batch_embeddings)

        logger.info(
            codes.EMBEDDINGS_GENERATED,
            count=len(all_embeddings),
            message=codes.MSG_EMBEDDINGS_GENERATED,
        )

        return all_embeddings

    def _process_batch(self, batch: List[str], batch_num: int) -> List[List[float]]:
        """
        Process a single batch of texts to generate embeddings.

        Args:
            batch: Batch of texts to process
            batch_num: Batch number for logging

        Returns:
            List of embedding vectors for the batch
        """
        logger.debug(
            codes.EMBEDDINGS_BATCH_PROCESSING,
            batch_num=batch_num,
            batch_size=len(batch),
        )

        try:
            result = genai.embed_content(
                model=self.model,
                content=batch,
                task_type=self.task_type,
                title=self.title if self.title else None,
            )

            return result.get(constants.EMBEDDING_KEY, [])

        except Exception as e:
            logger.error(
                codes.EMBEDDINGS_ERROR, batch_num=batch_num, error=str(e), exc_info=True
            )
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.

        Uses query-specific task type which may optimize differently
        than document embeddings.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        logger.debug(codes.EMBEDDINGS_GENERATING, count=1, type="query")

        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type=constants.TASK_TYPE_QUERY,
                title=self.title if self.title else None,
            )

            embedding = result.get(constants.EMBEDDING_KEY)

            logger.debug(
                codes.EMBEDDINGS_GENERATED, dimension=len(embedding) if embedding else 0
            )

            return embedding

        except Exception as e:
            logger.error(codes.EMBEDDINGS_ERROR, error=str(e), exc_info=True)
            raise

    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.

        Returns:
            Embedding dimension (768 for text-embedding-004)
        """
        return self.dimension
