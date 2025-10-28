"""
Query service for RAG operations.

Handles query processing through the RAG chain with lazy initialization.
"""

from typing import Dict, Any, Optional

from config import Config
from logger import get_logger
from utils.singleton import SingletonMeta
from app.chain_rag.chain import RAGChain
import constants
import trace.codes as codes


logger = get_logger(__name__)


class QueryService(metaclass=SingletonMeta):
    """
    Service for processing RAG queries.
    
    This service is a singleton - only one instance exists per process.
    The RAG chain is initialized lazily on first query.
    """
    
    def __init__(self):
        """
        Initialize query service.
        
        Due to singleton pattern, this only runs once per process.
        """
        if hasattr(self, '_initialized'):
            return
        
        logger.info(codes.QUERY_SERVICE_INITIALIZING)
        
        self._config: Optional[Config] = None
        self._rag_chain: Optional[RAGChain] = None
        
        self._initialized = True
        
        logger.info(
            codes.QUERY_SERVICE_INITIALIZED,
            msg=constants.MSG_QUERY_SERVICE_INITIALIZED
        )
    
    def _ensure_config_initialized(self) -> None:
        """Ensure config is initialized (lazy initialization)."""
        if self._config is None:
            self._config = Config()
    
    def _ensure_rag_chain_initialized(self) -> None:
        """
        Ensure RAG chain is initialized (lazy initialization).
        
        Raises:
            RuntimeError: If RAG chain initialization fails
        """
        if self._rag_chain is not None:
            return
        
        self._ensure_config_initialized()
        
        try:
            logger.info(codes.RAG_CHAIN_INITIALIZING)
            self._rag_chain = RAGChain(config=self._config)
            logger.info(codes.RAG_CHAIN_INITIALIZED)
        except Exception as e:
            logger.error(
                codes.RAG_CHAIN_INIT_FAILED,
                error=str(e),
                exc_info=True
            )
            raise RuntimeError(constants.ERROR_RAG_CHAIN_INITIALIZATION_FAILED) from e
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a query through the RAG chain.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing:
                - answer: Generated answer
                - sources: List of source documents
                - has_answer: Whether answer was found
                - query: Original question
                
        Raises:
            RuntimeError: If RAG chain not initialized
            ValueError: If query processing fails
        """
        logger.info(
            codes.QUERY_API_REQUEST_RECEIVED,
            msg=constants.MSG_QUERY_RECEIVED,
            question=question
        )
        
        self._ensure_rag_chain_initialized()
        
        if self._rag_chain is None:
            logger.error(
                codes.RAG_CHAIN_NOT_INITIALIZED,
                error=constants.ERROR_RAG_CHAIN_NOT_INITIALIZED
            )
            raise RuntimeError(constants.ERROR_RAG_CHAIN_NOT_INITIALIZED)
        
        try:
            logger.info(
                codes.QUERY_API_PROCESSING,
                msg=constants.MSG_QUERY_PROCESSING
            )
            
            result = self._rag_chain.query(question)
            
            logger.info(
                codes.QUERY_API_COMPLETED,
                msg=constants.MSG_QUERY_COMPLETED,
                has_answer=result.get(constants.RESPONSE_KEY_HAS_ANSWER, False)
            )
            
            return result
            
        except Exception as e:
            logger.error(
                codes.QUERY_API_FAILED,
                error=str(e),
                question=question,
                exc_info=True
            )
            raise ValueError(constants.ERROR_QUERY_PROCESSING_FAILED) from e
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check RAG system health.
        
        Returns:
            Dictionary containing:
                - rag_initialized: Whether RAG chain is initialized
                - provider: LLM provider name
                - model: LLM model name
        """
        self._ensure_config_initialized()
        
        return {
            "rag_initialized": self._rag_chain is not None,
            "provider": self._config.rag.provider,
            "model": self._get_model_name()
        }
    
    def _get_model_name(self) -> str:
        """
        Get the configured LLM model name based on provider.
        
        Returns:
            Model name string
        """
        if self._config.rag.provider == constants.LLM_PROVIDER_GOOGLE:
            return self._config.rag.google.model
        
        if self._config.rag.provider == constants.LLM_PROVIDER_OPENAI:
            return self._config.rag.openai.model
        
        if self._config.rag.provider == constants.LLM_PROVIDER_ANTHROPIC:
            return self._config.rag.anthropic.model
        
        return "unknown"

