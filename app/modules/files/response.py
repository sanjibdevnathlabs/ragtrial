"""
Files module response models.

Contains Pydantic models for file listing and metadata responses.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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
                "updated_at": 1700000000000,
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
                        "indexed": False,
                    }
                ],
                "count": 2,
                "backend": "local",
            }
        }
    )

    files: list[dict] = Field(..., description="List of files with metadata")
    count: int = Field(..., description="Total file count")
    backend: str = Field(..., description="Storage backend")
