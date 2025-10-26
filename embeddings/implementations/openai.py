"""
OpenAI embeddings implementation.

Uses OpenAI's text-embedding models (text-embedding-3-small, text-embedding-3-large).
"""

from typing import List, TYPE_CHECKING

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
            error_msg = "openai package not installed. Run: pip install openai"
            logger.error(codes.EMBEDDINGS_ERROR, message=error_msg)
            raise ImportError(error_msg)
        
        self.config = config
        self.model = config.embeddings.openai.model
        self.batch_size = config.embeddings.openai.batch_size
        self.dimensions = config.embeddings.openai.dimensions
        self.dimension = self.dimensions  # For get_dimension()
        self.verify_ssl = config.embeddings.openai.verify_ssl
        
        # Initialize OpenAI client with SSL configuration
        import httpx
        if self.verify_ssl:
            # Use certifi's certificate bundle (fixes macOS SSL issues)
            import certifi
            http_client = httpx.Client(verify=certifi.where())
            self.client = OpenAI(
                api_key=config.embeddings.openai.api_key,
                http_client=http_client
            )
            logger.info(
                codes.EMBEDDINGS_INITIALIZING,
                provider="openai",
                message="Using certifi certificate bundle for SSL verification"
            )
        else:
            # Disable SSL verification for development
            http_client = httpx.Client(verify=False)
            self.client = OpenAI(
                api_key=config.embeddings.openai.api_key,
                http_client=http_client
            )
            logger.warning(
                codes.CONFIG_WARNING,
                message="SSL verification disabled for OpenAI API (development only)"
            )
        
        logger.info(
            codes.EMBEDDINGS_INITIALIZED,
            provider="openai",
            model=self.model,
            dimension=self.dimension,
            message=codes.MSG_EMBEDDINGS_INITIALIZED
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
            codes.EMBEDDINGS_GENERATING,
            count=len(texts),
            batch_size=self.batch_size
        )
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            logger.debug(
                codes.EMBEDDINGS_BATCH_PROCESSING,
                batch_num=i // self.batch_size + 1,
                batch_size=len(batch)
            )
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimensions
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(
                    codes.EMBEDDINGS_ERROR,
                    batch_num=i // self.batch_size + 1,
                    error=str(e),
                    exc_info=True
                )
                raise
        
        logger.info(
            codes.EMBEDDINGS_GENERATED,
            count=len(all_embeddings),
            message=codes.MSG_EMBEDDINGS_GENERATED
        )
        
        return all_embeddings
    
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

