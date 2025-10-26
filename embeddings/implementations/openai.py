"""
OpenAI embeddings implementation.

Uses OpenAI's text-embedding models (text-embedding-3-small, text-embedding-3-large).
"""

from typing import List, TYPE_CHECKING

import constants
from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class OpenAIEmbeddings:
    """
    OpenAI embeddings provider implementation.
    
    Uses OpenAI's API for creating embeddings with text-embedding-3 models.
    Supports configurable dimensions for efficiency.
    
    Attributes:
        config: Application configuration
        client: OpenAI client instance
        model: Model name (e.g., "text-embedding-3-small")
        batch_size: Number of texts to process in one batch
        dimensions: Optional dimension reduction
        dimension: Embedding dimension
    """
    
    def __init__(self, config: "Config"):
        """
        Initialize OpenAI embeddings provider.
        
        Args:
            config: Application configuration containing OpenAI API settings
        """
        logger.info(codes.EMBEDDINGS_INITIALIZING, provider="openai")
        
        try:
            from openai import OpenAI
        except ImportError:
            logger.error(codes.EMBEDDINGS_ERROR, message=constants.ERROR_OPENAI_NOT_INSTALLED)
            raise ImportError(constants.ERROR_OPENAI_NOT_INSTALLED)
        
        self.config = config
        self.model = config.embeddings.openai.model
        self.batch_size = config.embeddings.openai.batch_size
        self.dimensions = config.embeddings.openai.dimensions
        self.dimension = self.dimensions
        self.verify_ssl = config.embeddings.openai.verify_ssl
        
        self.client = self._initialize_client(OpenAI, config.embeddings.openai.api_key)
        
        logger.info(
            codes.EMBEDDINGS_INITIALIZED,
            provider="openai",
            model=self.model,
            dimension=self.dimension,
            message=codes.MSG_EMBEDDINGS_INITIALIZED
        )
    
    def _initialize_client(self, OpenAI, api_key: str):
        """Initialize OpenAI client with SSL configuration."""
        import httpx
        
        if not self.verify_ssl:
            http_client = httpx.Client(verify=False)
            client = OpenAI(api_key=api_key, http_client=http_client)
            logger.warning(
                codes.CONFIG_WARNING,
                message=constants.MSG_SSL_DISABLED_DEV
            )
            return client
        
        import certifi
        http_client = httpx.Client(verify=certifi.where())
        client = OpenAI(api_key=api_key, http_client=http_client)
        logger.info(
            codes.EMBEDDINGS_INITIALIZING,
            provider="openai",
            message=constants.MSG_SSL_CERTIFI_BUNDLE
        )
        return client
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        logger.info(
            codes.EMBEDDINGS_GENERATING,
            count=len(texts),
            batch_size=self.batch_size
        )
        
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            
            batch_embeddings = self._process_batch(batch, batch_num)
            all_embeddings.extend(batch_embeddings)
        
        logger.info(
            codes.EMBEDDINGS_GENERATED,
            count=len(all_embeddings),
            message=codes.MSG_EMBEDDINGS_GENERATED
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
            batch_size=len(batch)
        )
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
                dimensions=self.dimensions
            )
            
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(
                codes.EMBEDDINGS_ERROR,
                batch_num=batch_num,
                error=str(e),
                exc_info=True
            )
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        logger.debug(codes.EMBEDDINGS_GENERATING, count=1, type="query")
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )
            
            embedding = response.data[0].embedding
            
            logger.debug(
                codes.EMBEDDINGS_GENERATED,
                dimension=len(embedding)
            )
            
            return embedding
            
        except Exception as e:
            logger.error(
                codes.EMBEDDINGS_ERROR,
                error=str(e),
                exc_info=True
            )
            raise
    
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        return self.dimension

