"""
Pydantic models for API request/response validation.

Defines schemas for file upload and query operations.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

import constants


class UploadResponse(BaseModel):
    """Response model for successful file upload."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "filename": "document.pdf",
                "path": "source_docs/document.pdf",
                "size": 1048576,
                "backend": "local"
            }
        }
    )
    
    success: bool = Field(..., description="Upload success status")
    filename: str = Field(..., description="Name of uploaded file")
    path: str = Field(..., description="Storage path of uploaded file")
    size: int = Field(..., description="File size in bytes")
    backend: str = Field(..., description="Storage backend used (local/s3)")


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "File size exceeds maximum allowed",
                "error_code": "FILE_TOO_LARGE"
            }
        }
    )
    
    success: bool = Field(False, description="Upload success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")


class FileMetadataResponse(BaseModel):
    """Response model for file metadata."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.pdf",
                "size": "1048576",
                "modified_time": "2025-10-28T00:00:00",
                "path": "source_docs/document.pdf"
            }
        }
    )
    
    filename: str = Field(..., description="File name")
    size: str = Field(..., description="File size")
    modified_time: str = Field(..., description="Last modified time")
    path: Optional[str] = Field(None, description="File path (local storage)")
    etag: Optional[str] = Field(None, description="ETag (S3 storage)")


class FileListResponse(BaseModel):
    """Response model for file listing."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "files": ["doc1.pdf", "doc2.txt"],
                "count": 2,
                "backend": "local"
            }
        }
    )
    
    files: list[str] = Field(..., description="List of file names")
    count: int = Field(..., description="Total file count")
    backend: str = Field(..., description="Storage backend")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "storage_backend": "local",
                "version": "1.0.0"
            }
        }
    )
    
    status: str = Field(..., description="Service status")
    storage_backend: str = Field(..., description="Configured storage backend")
    version: str = Field(..., description="API version")


class QueryRequest(BaseModel):
    """Request model for RAG query."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "What is retrieval-augmented generation?"
            }
        }
    )
    
    question: str = Field(
        ...,
        min_length=constants.MIN_QUERY_LENGTH,
        max_length=constants.MAX_QUERY_LENGTH_API,
        description="Question to ask the RAG system"
    )
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question is not empty or too short."""
        if not v or not v.strip():
            raise ValueError(constants.ERROR_QUERY_EMPTY)
        
        if len(v.strip()) < constants.MIN_QUERY_LENGTH:
            raise ValueError(constants.ERROR_QUERY_TOO_SHORT)
        
        return v.strip()


class SourceDocument(BaseModel):
    """Model for source document metadata."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.pdf",
                "chunk_index": 0,
                "content": "Retrieval-augmented generation (RAG) is..."
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
                        "content": "RAG combines retrieval..."
                    }
                ],
                "has_answer": True,
                "query": "What is RAG?"
            }
        }
    )
    
    success: bool = Field(True, description="Query success status")
    answer: str = Field(..., description="Generated answer")
    sources: list[SourceDocument] = Field(..., description="Source documents used")
    has_answer: bool = Field(..., description="Whether answer was found in documents")
    query: str = Field(..., description="Original query")

