"""
Query module response models.

Contains Pydantic models for RAG query responses.
"""

from pydantic import BaseModel, ConfigDict, Field


class SourceDocument(BaseModel):
    """Model for source document metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.pdf",
                "chunk_index": 0,
                "content": "Retrieval-augmented generation (RAG) is...",
            }
        }
    )

    filename: str = Field(..., description="Source document filename")
    chunk_index: int = Field(..., description="Chunk index in document")
    content: str = Field(..., description="Chunk content")


class QueryResponse(BaseModel):
    """Response model for successful RAG query."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "answer": "Retrieval-augmented generation is...",
                "sources": [
                    {
                        "filename": "rag_paper.pdf",
                        "chunk_index": 0,
                        "content": "RAG combines retrieval...",
                    }
                ],
                "has_answer": True,
                "query": "What is RAG?",
            }
        }
    )

    success: bool = Field(True, description="Query success status")
    answer: str = Field(..., description="Generated answer")
    sources: list[SourceDocument] = Field(..., description="Source documents used")
    has_answer: bool = Field(..., description="Whether answer was found in documents")
    query: str = Field(..., description="Original query")
