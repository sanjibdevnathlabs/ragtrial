"""
Anthropic (Voyage AI) embeddings implementation.

Uses Voyage AI's embedding models (recommended by Anthropic).
"""

from typing import List, TYPE_CHECKING

from logger import get_logger
from trace import codes

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
            error_msg = "voyageai package not installed. Run: pip install voyageai"
            logger.error(codes.EMBEDDINGS_ERROR, message=error_msg)
            raise ImportError(error_msg)
        
        self.config = config
        self.model = config.embeddings.anthropic.model
        self.input_type = config.embeddings.anthropic.input_type
        self.batch_size = config.embeddings.anthropic.batch_size
        self.dimension = config.embeddings.dimension
        self.verify_ssl = config.embeddings.anthropic.verify_ssl
        
        # Handle SSL verification for Voyage AI client
        if not self.verify_ssl:
            # Disable SSL verification for development
            import ssl
            import urllib3
            
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Monkey-patch SSL context to disable verification
            import requests
            original_request = requests.Session.request
            
            def patched_request(self, method, url, **kwargs):
                kwargs['verify'] = False
                return original_request(self, method, url, **kwargs)
            
            requests.Session.request = patched_request
            
            logger.warning(
                codes.CONFIG_WARNING,
                message="SSL verification disabled for Voyage AI API (development only)"
            )
        else:
            # Use certifi's certificate bundle (fixes macOS SSL issues)
            import certifi
            import os
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
            logger.info(
                codes.EMBEDDINGS_INITIALIZING,
                provider="anthropic",
                message="Using certifi certificate bundle for SSL verification"
            )
        
        # Initialize Voyage AI client
        self.client = voyageai.Client(
            api_key=config.embeddings.anthropic.api_key
        )
        
        logger.info(
            codes.EMBEDDINGS_INITIALIZED,
            provider="anthropic",
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
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type=self.input_type
                )
                
                batch_embeddings = response.embeddings
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
                input_type="query"  # Use query-specific input type
            )
            
            embedding = response.embeddings[0]
            
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
            Embedding dimension (1024 for voyage-2, 1536 for voyage-large-2)
        """
        return self.dimension

