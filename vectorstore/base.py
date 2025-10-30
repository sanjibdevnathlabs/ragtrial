"""
Base protocol (interface) for vector store providers.

All vectorstore implementations must follow this protocol to ensure
a uniform API regardless of provider.
"""

from typing import Any, Dict, List, Optional, Protocol


class VectorStoreProtocol(Protocol):
    """
    Abstract interface that all vector store providers must implement.

    This protocol defines the contract for vector database operations,
    ensuring consistent behavior across ChromaDB, Pinecone, Qdrant, etc.
    """

    def initialize(self) -> None:
        """
        Initialize the vector store and create/get collection.

        This should:
        - Connect to the database
        - Create collection if it doesn't exist
        - Get collection if it already exists

        Example:
            vectorstore.initialize()
        """
        ...

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            texts: List of document text strings
            metadatas: Optional list of metadata dicts (one per document)
            ids: Optional list of document IDs (generated if not provided)

        Example:
            vectorstore.add_documents(
                texts=["doc 1", "doc 2"],
                metadatas=[{"source": "a.pdf"}, {"source": "b.pdf"}],
                ids=["doc_1", "doc_2"]
            )
        """
        ...

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar documents.

        Args:
            query_text: Text to search for
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            List of result dicts containing:
                - id: Document ID
                - text: Document text
                - metadata: Document metadata
                - distance: Similarity score

        Example:
            results = vectorstore.query(
                query_text="What is RAG?",
                n_results=5,
                where={"source": "manual.pdf"}
            )
        """
        ...

    def delete(self, ids: List[str]) -> None:
        """
        Delete documents from the vector store.

        Args:
            ids: List of document IDs to delete

        Example:
            vectorstore.delete(["doc_1", "doc_2"])
        """
        ...

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dict containing stats like:
                - count: Number of documents
                - collection_name: Name of collection
                - etc.

        Example:
            stats = vectorstore.get_stats()
            logger.info(codes.VECTORSTORE_STATS, count=stats['count'])
        """
        ...

    def clear(self) -> None:
        """
        Delete all documents from the collection.

        Warning: This is destructive and cannot be undone!

        Example:
            vectorstore.clear()
        """
        ...

    def check_health(self) -> bool:
        """
        Fast health check to verify vectorstore connectivity.

        Should be a lightweight operation (ping/heartbeat).
        Must complete in < 100ms for optimal performance.

        Returns:
            True if vectorstore is responsive, False otherwise

        Example:
            is_healthy = vectorstore.check_health()
        """
        ...
