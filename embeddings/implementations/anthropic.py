"""
Anthropic (Voyage AI) embeddings implementation.

Uses Voyage AI's embedding models (recommended by Anthropic).
"""

from trace import codes
from typing import TYPE_CHECKING, List

import constants
from logger import get_logger

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class AnthropicEmbeddings:
    """
    Anthropic (Voyage AI) embeddings provider implementation.

    Uses Voyage AI's API for creating embeddings (recommended by Anthropic
    for use with Claude). Supports voyage-2 and voyage-large-2 models.

    Attributes:
        config: Application configuration
        client: Voyage AI client instance
        model: Model name (e.g., "voyage-2")
        input_type: Input type (document or query)
        batch_size: Number of texts to process in one batch
        dimension: Embedding dimension
    """

    def __init__(self, config: "Config"):
        """
        Initialize Anthropic (Voyage AI) embeddings provider.

        Args:
            config: Application configuration containing Voyage AI API settings
        """
        logger.info(codes.EMBEDDINGS_INITIALIZING, provider="anthropic")

        try:
            import voyageai
        except ImportError:
            logger.error(
                codes.EMBEDDINGS_ERROR, message=constants.ERROR_VOYAGEAI_NOT_INSTALLED
            )
            raise ImportError(constants.ERROR_VOYAGEAI_NOT_INSTALLED)

        self.config = config
        self.model = config.embeddings.anthropic.model
        self.input_type = config.embeddings.anthropic.input_type
        self.batch_size = config.embeddings.anthropic.batch_size
        self.dimension = config.embeddings.dimension
        self.verify_ssl = config.embeddings.anthropic.verify_ssl

        # Handle SSL verification for Voyage AI client
        if not self.verify_ssl:
            pass

            import requests
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            original_request = requests.Session.request

            def patched_request(self, method, url, **kwargs):
                kwargs["verify"] = False
                return original_request(self, method, url, **kwargs)

            requests.Session.request = patched_request

            logger.warning(
                codes.CONFIG_WARNING, message=constants.MSG_SSL_DISABLED_VOYAGEAI_DEV
            )

            self.client = voyageai.Client(api_key=config.embeddings.anthropic.api_key)

            logger.info(
                codes.EMBEDDINGS_INITIALIZED,
                provider="anthropic",
                model=self.model,
                dimension=self.dimension,
                message=codes.MSG_EMBEDDINGS_INITIALIZED,
            )
            return

        # Use certifi's certificate bundle (fixes macOS SSL issues)
        import os

        import certifi

        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
        logger.info(
            codes.EMBEDDINGS_INITIALIZING,
            provider="anthropic",
            message=constants.MSG_SSL_CERTIFI_BUNDLE,
        )

        self.client = voyageai.Client(api_key=config.embeddings.anthropic.api_key)

        logger.info(
            codes.EMBEDDINGS_INITIALIZED,
            provider="anthropic",
            model=self.model,
            dimension=self.dimension,
            message=codes.MSG_EMBEDDINGS_INITIALIZED,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

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
            response = self.client.embed(
                texts=batch, model=self.model, input_type=self.input_type
            )

            return response.embeddings

        except Exception as e:
            logger.error(
                codes.EMBEDDINGS_ERROR, batch_num=batch_num, error=str(e), exc_info=True
            )
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.

        Uses "query" input type for queries.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        logger.debug(codes.EMBEDDINGS_GENERATING, count=1, type="query")

        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="query",  # Use query-specific input type
            )

            embedding = response.embeddings[0]

            logger.debug(codes.EMBEDDINGS_GENERATED, dimension=len(embedding))

            return embedding

        except Exception as e:
            logger.error(codes.EMBEDDINGS_ERROR, error=str(e), exc_info=True)
            raise

    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.

        Returns:
            Embedding dimension (1024 for voyage-2, 1536 for voyage-large-2)
        """
        return self.dimension
