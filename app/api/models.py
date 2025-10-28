"""
Pydantic models for API request/response validation.

Defines schemas for file upload and query operations.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

import constants


class UploadResponse(BaseModel):
    """Response model for successful file upload."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "document.pdf",
                "path": "source_docs/550e8400-e29b-41d4-a716-446655440000.pdf",
                "size": 1048576,
                "file_type": "pdf",
                "checksum": "abc123...",
                "backend": "local",
                "indexed": False
            }
        }
    )
    
    success: bool = Field(..., description="Upload success status")
    file_id: str = Field(..., description="Unique file ID (UUID)")
    filename: str = Field(..., description="Original filename")
    path: str = Field(..., description="Storage path (UUID-based)")
    size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File extension without dot")
    checksum: str = Field(..., description="SHA-256 checksum")
    backend: str = Field(..., description="Storage backend (local/s3)")
    indexed: bool = Field(False, description="Indexed in vectorstore")


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


class FileUploadResult(BaseModel):
    """Result for a single file upload in batch."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.pdf",
                "success": True,
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "path": "source_docs/550e8400-e29b-41d4-a716-446655440000.pdf",
                "size": 1048576,
                "file_type": "pdf",
                "checksum": "abc123...",
                "backend": "local",
                "indexed": False
            }
        }
    )
    
    filename: str = Field(..., description="Original filename")
    success: bool = Field(..., description="Upload success status")
    file_id: Optional[str] = Field(None, description="Unique file ID (UUID)")
    path: Optional[str] = Field(None, description="Storage path (UUID-based)")
    size: Optional[int] = Field(None, description="File size in bytes")
    file_type: Optional[str] = Field(None, description="File extension without dot")
    checksum: Optional[str] = Field(None, description="SHA-256 checksum")
    backend: Optional[str] = Field(None, description="Storage backend (local/s3)")
    indexed: Optional[bool] = Field(None, description="Indexed in vectorstore")
    error: Optional[str] = Field(None, description="Error message if failed")
    error_code: Optional[str] = Field(None, description="Error code if failed")


class BatchUploadResponse(BaseModel):
    """Response model for batch file upload."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 3,
                "successful": 2,
                "failed": 1,
                "results": [
                    {
                        "filename": "doc1.pdf",
                        "success": True,
                        "file_id": "550e8400-e29b-41d4-a716-446655440000",
                        "path": "source_docs/550e8400-e29b-41d4-a716-446655440000.pdf",
                        "size": 1048576,
                        "file_type": "pdf",
                        "checksum": "abc123...",
                        "backend": "local",
                        "indexed": False
                    },
                    {
                        "filename": "doc2.pdf",
                        "success": False,
                        "error": "File too large",
                        "error_code": "FILE_TOO_LARGE"
                    }
                ]
            }
        }
    )
    
    total: int = Field(..., description="Total files attempted")
    successful: int = Field(..., description="Number of successful uploads")
    failed: int = Field(..., description="Number of failed uploads")
    results: List[FileUploadResult] = Field(..., description="Individual upload results")


class FileMetadataResponse(BaseModel):
    """Response model for file metadata."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "document.pdf",
                "file_path": "source_docs/550e8400-e29b-41d4-a716-446655440000.pdf",
                "file_type": "pdf",
                "file_size": 1048576,
                "checksum": "abc123...",
                "storage_backend": "local",
                "indexed": False,
                "created_at": 1700000000000,
                "updated_at": 1700000000000
            }
        }
    )
    
    file_id: str = Field(..., description="Unique file ID (UUID)")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Storage path (UUID-based)")
    file_type: str = Field(..., description="File extension without dot")
    file_size: int = Field(..., description="File size in bytes")
    checksum: str = Field(..., description="SHA-256 checksum")
    storage_backend: str = Field(..., description="Storage backend")
    indexed: bool = Field(..., description="Indexed in vectorstore")
    created_at: int = Field(..., description="Creation timestamp (ms)")
    updated_at: int = Field(..., description="Update timestamp (ms)")
    indexed_at: Optional[int] = Field(None, description="Index timestamp (ms)")


class FileListResponse(BaseModel):
    """Response model for file listing."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "files": [
                    {
                        "file_id": "550e8400-e29b-41d4-a716-446655440000",
                        "filename": "doc1.pdf",
                        "file_size": 1048576,
                        "indexed": False
                    }
                ],
                "count": 2,
                "backend": "local"
            }
        }
    )
    
    files: list[dict] = Field(..., description="List of files with metadata")
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

