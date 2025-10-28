"""
Upload module response models.

Contains Pydantic models for upload API responses.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


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

