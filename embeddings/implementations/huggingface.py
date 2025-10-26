"""
HuggingFace embeddings implementation.

Uses sentence-transformers models for local embedding generation.
"""

from typing import List, TYPE_CHECKING

from logger import get_logger
from trace import codes

if TYPE_CHECKING:
    from config import Config

logger = get_logger(__name__)


class HuggingFaceEmbeddings:
    """
    HuggingFace embeddings provider implementation.
    
    Uses sentence-transformers library for local embedding generation.
    Models are downloaded and cached locally.
    
    Attributes:
        config: Application configuration
        model: SentenceTransformer model instance
        model_name: Name of the model
        dimension: Embedding dimension
    """
    
    def __init__(self, config: "Config"):
        """
        Initialize HuggingFace embeddings provider.
        
        Args:
            config: Application configuration containing HuggingFace settings
        """
        logger.info(codes.EMBEDDINGS_INITIALIZING, provider="huggingface")
        
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            error_msg = "sentence-transformers package not installed. Run: pip install sentence-transformers"
            logger.error(codes.EMBEDDINGS_ERROR, message=error_msg)
            raise ImportError(error_msg)
        
        self.config = config
        self.model_name = config.embeddings.huggingface.model_name
        self.cache_folder = config.embeddings.huggingface.cache_folder
        self.device = config.embeddings.huggingface.device
        
        # Load model
        logger.info(
            "loading_model",
            model_name=self.model_name,
            device=self.device
        )
        
        self.model = SentenceTransformer(
            self.model_name,
            cache_folder=self.cache_folder,
            device=self.device
        )
        
        # Get dimension from model
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(
            codes.EMBEDDINGS_INITIALIZED,
            provider="huggingface",
            model=self.model_name,
            dimension=self.dimension,
            device=self.device,
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
            count=len(texts)
        )
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=False,
                show_progress_bar=False
            )
            
            # Convert to list of lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            logger.info(
                codes.EMBEDDINGS_GENERATED,
                count=len(embeddings_list),
                message=codes.MSG_EMBEDDINGS_GENERATED
            )
            
            return embeddings_list
            
        except Exception as e:
            logger.error(
                codes.EMBEDDINGS_ERROR,
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
            embedding = self.model.encode(
                text,
                convert_to_numpy=False,
                show_progress_bar=False
            )
            
            embedding_list = embedding.tolist()
            
            logger.debug(
                codes.EMBEDDINGS_GENERATED,
                dimension=len(embedding_list)
            )
            
            return embedding_list
            
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

