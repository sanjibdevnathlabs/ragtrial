"""
Main RAG chain implementation.

Orchestrates document retrieval, prompt formatting, and LLM generation.
"""

from typing import Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from config import Config
from app.simple_rag.retriever import DocumentRetriever
from app.simple_rag.prompts import create_rag_prompt, format_context
from app.simple_rag.response import ResponseFormatter
from app.security.guardrails import GuardrailsManager, GuardrailsConfig
from logger import get_logger
from trace import codes
import constants

logger = get_logger(__name__)


class RAGChain:
    """
    Simple RAG chain using LangChain.
    
    Retrieves relevant documents from vectorstore and generates
    answers using LLM with proper source citations.
    """
    
    def __init__(self, config: Config):
        """
        Initialize RAG chain with configuration.
        
        Args:
            config: Application configuration
            
        Raises:
            RuntimeError: If chain initialization fails
        """
        logger.info(codes.RAG_CHAIN_INITIALIZING)
        
        try:
            self.config = config
            self.retriever = DocumentRetriever(config)
            self.prompt = create_rag_prompt()
            self._init_llm()
            
            # Initialize security guardrails
            self.guardrails = GuardrailsManager(GuardrailsConfig(
                enable_input_validation=True,
                enable_injection_detection=True,
                enable_output_validation=True,
                strict_mode=True
            ))
            
            logger.info(
                codes.RAG_CHAIN_INITIALIZED,
                message=constants.MSG_RAG_CHAIN_INITIALIZED
            )
            
        except Exception as e:
            logger.error(
                codes.RAG_CHAIN_INITIALIZING,
                error=str(e),
                exc_info=True
            )
            raise RuntimeError(constants.ERROR_RAG_CHAIN_INIT_FAILED) from e
    
    def _init_llm(self) -> None:
        """
        Initialize LLM based on configuration provider.
        
        Supports: Google (Gemini), OpenAI (GPT), Anthropic (Claude)
        """
        provider = self.config.rag.provider.lower()
        
        if provider == constants.LLM_PROVIDER_GOOGLE:
            self._init_google_llm()
            return
        
        if provider == constants.LLM_PROVIDER_OPENAI:
            self._init_openai_llm()
            return
        
        if provider == constants.LLM_PROVIDER_ANTHROPIC:
            self._init_anthropic_llm()
            return
        
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def _init_google_llm(self) -> None:
        """Initialize Google Gemini LLM."""
        config = self.config.rag.google
        # Only pass API key if explicitly set, otherwise LangChain picks from env
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,  # Gemini uses max_output_tokens
        }
        if config.api_key:
            kwargs["google_api_key"] = config.api_key
        self.llm = ChatGoogleGenerativeAI(**kwargs)
    
    def _init_openai_llm(self) -> None:
        """Initialize OpenAI GPT LLM."""
        config = self.config.rag.openai
        # Only pass API key if explicitly set, otherwise LangChain picks from env
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        if config.api_key:
            kwargs["api_key"] = config.api_key
        self.llm = ChatOpenAI(**kwargs)
    
    def _init_anthropic_llm(self) -> None:
        """Initialize Anthropic Claude LLM."""
        config = self.config.rag.anthropic
        # Only pass API key if explicitly set, otherwise LangChain picks from env
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        if config.api_key:
            kwargs["api_key"] = config.api_key
        self.llm = ChatAnthropic(**kwargs)
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process query and return answer with sources.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer, sources, and metadata
            
        Raises:
            ValueError: If question is invalid or blocked by guardrails
            RuntimeError: If query processing fails
        """
        if not question or not question.strip():
            raise ValueError(constants.ERROR_RAG_INVALID_QUERY)
        
        logger.info(codes.RAG_QUERY_RECEIVED, query=question)
        
        try:
            # Validate input with guardrails
            validation_result = self.guardrails.validate_input(question)
            
            if not validation_result[constants.VALIDATION_KEY_IS_SAFE]:
                logger.warning(
                    codes.RAG_QUERY_FAILED,
                    message=constants.MSG_QUERY_BLOCKED,
                    violations=validation_result[constants.VALIDATION_KEY_VIOLATIONS],
                    threat_level=validation_result[constants.VALIDATION_KEY_THREAT_LEVEL]
                )
                raise ValueError(validation_result[constants.VALIDATION_KEY_ERROR_MESSAGE])
            
            # Use sanitized query
            sanitized_question = validation_result[constants.VALIDATION_KEY_SANITIZED_QUERY]
            
            return self._process_query(sanitized_question)
            
        except ValueError:
            raise
            
        except Exception as e:
            logger.error(
                codes.RAG_QUERY_FAILED,
                query=question,
                error=str(e),
                exc_info=True
            )
            raise RuntimeError(constants.ERROR_RAG_QUERY_FAILED) from e
    
    def _process_query(self, question: str) -> Dict[str, Any]:
        """
        Execute RAG query pipeline.
        
        Args:
            question: User's question
            
        Returns:
            Formatted response dictionary
        """
        logger.info(codes.RAG_QUERY_PROCESSING, query=question)
        
        documents = self.retriever.retrieve(question)
        
        if not documents:
            logger.warning(
                codes.RAG_NO_DOCUMENTS_FOUND,
                query=question,
                message=constants.MSG_RAG_NO_RELEVANT_DOCS
            )
            return ResponseFormatter.format_response(
                answer=constants.MSG_RAG_NO_RELEVANT_DOCS,
                source_documents=[],
                query=question
            )
        
        answer = self._generate_answer(question, documents)
        response = ResponseFormatter.format_response(answer, documents, question)
        
        logger.info(
            codes.RAG_QUERY_COMPLETED,
            query=question,
            has_answer=response[constants.RESPONSE_KEY_HAS_ANSWER],
            source_count=len(documents)
        )
        
        return response
    
    def _generate_answer(self, question: str, documents) -> str:
        """
        Generate answer using LLM.
        
        Args:
            question: User's question
            documents: Retrieved documents
            
        Returns:
            Generated answer text
            
        Raises:
            RuntimeError: If LLM generation fails
        """
        context = format_context(documents)
        
        logger.info(codes.RAG_LLM_GENERATING, query=question)
        
        try:
            messages = self.prompt.format_messages(
                context=context,
                question=question
            )
            
            response = self.llm.invoke(messages)
            answer = response.content
            
            logger.info(codes.RAG_LLM_GENERATED, query=question)
            
            # Validate output with guardrails
            output_validation = self.guardrails.validate_output(answer)
            
            if not output_validation[constants.VALIDATION_KEY_IS_SAFE]:
                logger.error(
                    codes.RAG_LLM_FAILED,
                    message=constants.MSG_LLM_OUTPUT_BLOCKED,
                    violations=output_validation[constants.VALIDATION_KEY_VIOLATIONS],
                    threat_level=output_validation[constants.VALIDATION_KEY_THREAT_LEVEL]
                )
                raise RuntimeError(constants.ERROR_OUTPUT_BLOCKED)
            
            return output_validation[constants.VALIDATION_KEY_VALIDATED_OUTPUT]
            
        except Exception as e:
            logger.error(
                codes.RAG_LLM_FAILED,
                query=question,
                error=str(e),
                exc_info=True
            )
            raise RuntimeError(constants.ERROR_RAG_LLM_FAILED) from e

