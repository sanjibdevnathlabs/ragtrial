"""
Google embeddings implementation using Google Generative AI.

Uses Google's text-embedding-004 model for generating embeddings.
"""

from typing import List, TYPE_CHECKING
import google.generativeai as genai

from logger import get_logger
from trace import codes

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
            message=codes.MSG_EMBEDDINGS_INITIALIZED
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
                # Generate embeddings for batch
                result = genai.embed_content(
                    model=self.model,
                    content=batch,
                    task_type=self.task_type,
                    title=self.title if self.title else None
                )
                
                # Extract embedding vectors
                batch_embeddings = result.get("embedding", [])
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
        
        Uses "retrieval_query" task type which may optimize differently
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
                task_type="retrieval_query",  # Use query-specific task type
                title=self.title if self.title else None
            )
            
            embedding = result.get("embedding")
            
            logger.debug(
                codes.EMBEDDINGS_GENERATED,
                dimension=len(embedding) if embedding else 0
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
            Embedding dimension (768 for text-embedding-004)
        """
        return self.dimension

