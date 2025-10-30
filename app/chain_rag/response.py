"""
Response formatter for RAG.

Formats LLM responses with source citations and metadata.
"""

from typing import Any, Dict, List

from langchain_core.documents import Document

import constants


class ResponseFormatter:
    """Formats RAG responses with sources and metadata."""

    @staticmethod
    def format_response(
        answer: str, source_documents: List[Document], query: str
    ) -> Dict[str, Any]:
        """
        Format RAG response with answer and sources.

        Args:
            answer: Generated answer from LLM
            source_documents: List of source Document objects
            query: Original query string

        Returns:
            Dictionary with formatted response
        """
        sources = ResponseFormatter._extract_sources(source_documents)
        has_answer = ResponseFormatter._check_has_answer(answer)

        return {
            constants.RESPONSE_KEY_ANSWER: answer,
            constants.RESPONSE_KEY_SOURCES: sources,
            constants.RESPONSE_KEY_QUERY: query,
            constants.RESPONSE_KEY_RETRIEVAL_COUNT: len(source_documents),
            constants.RESPONSE_KEY_HAS_ANSWER: has_answer,
        }

    @staticmethod
    def _extract_sources(documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Extract source information from documents.

        Args:
            documents: List of Document objects

        Returns:
            List of source dictionaries with metadata
        """
        if not documents:
            return []

        sources = []

        for doc in documents:
            # Extract filename from metadata for better UX
            filename = doc.metadata.get("filename", doc.metadata.get("source", "Unknown Document"))
            
            source_info = {
                "filename": filename,  # Promote filename to top level for easy access
                "content": doc.page_content[:500],  # Increased from 200 to 500 chars
                "metadata": doc.metadata,
            }
            sources.append(source_info)

        return sources

    @staticmethod
    def _check_has_answer(answer: str) -> bool:
        """
        Check if response contains an actual answer.

        Args:
            answer: Generated answer text

        Returns:
            Boolean indicating if answer exists
        """
        if not answer or not answer.strip():
            return False

        no_answer_phrases = [
            "don't have enough information",
            "cannot answer",
            "insufficient context",
            "no information provided",
            "no relevant documents",
        ]

        answer_lower = answer.lower()

        for phrase in no_answer_phrases:
            if phrase in answer_lower:
                return False

        return True
