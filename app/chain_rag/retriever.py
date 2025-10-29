"""
Document retriever for RAG.

Handles querying vectorstore and retrieving relevant documents.
"""

import trace.codes as codes
from typing import List

from langchain_core.documents import Document

import constants
from config import Config
from embeddings import create_embeddings
from logger import get_logger
from vectorstore import create_vectorstore

logger = get_logger(__name__)


class DocumentRetriever:
    """
    Retrieves relevant documents from vectorstore for RAG.

    Uses embeddings and vectorstore from configuration.
    """

    def __init__(self, config: Config):
        """
        Initialize retriever with configuration.

        Args:
            config: Application configuration
        """
        self.config = config
        self.embeddings = create_embeddings(config)
        self.vectorstore = create_vectorstore(config, self.embeddings)
        # Initialize vectorstore collection
        self.vectorstore.initialize()

        logger.info(
            codes.RAG_CHAIN_INITIALIZING,
            component="retriever",
            vectorstore=config.vectorstore.provider,
            embeddings=config.embeddings.provider,
        )

    def retrieve(
        self, query: str, k: int = constants.DEFAULT_RETRIEVAL_K
    ) -> List[Document]:
        """
        Retrieve relevant documents for query.

        Args:
            query: Search query string
            k: Number of documents to retrieve

        Returns:
            List of relevant Document objects

        Raises:
            ValueError: If query is empty or k is invalid
        """
        if not query or not query.strip():
            raise ValueError(constants.ERROR_RAG_INVALID_QUERY)

        if k < constants.MIN_RETRIEVAL_K or k > constants.MAX_RETRIEVAL_K:
            raise ValueError(
                f"k must be between {constants.MIN_RETRIEVAL_K} and "
                f"{constants.MAX_RETRIEVAL_K}"
            )

        logger.info(codes.RAG_RETRIEVAL_STARTED, query=query, k=k)

        try:
            results = self.vectorstore.query(query, n_results=k)

            # Convert dict results to Langchain Document objects
            documents = [
                Document(
                    page_content=result["text"], metadata=result.get("metadata", {})
                )
                for result in results
            ]

            logger.info(
                codes.RAG_RETRIEVAL_COMPLETED,
                query=query,
                document_count=len(documents),
            )

            return documents

        except Exception as e:
            logger.error(
                codes.RAG_RETRIEVAL_FAILED, query=query, error=str(e), exc_info=True
            )
            raise RuntimeError(constants.ERROR_RAG_RETRIEVAL_FAILED) from e
