"""
Storage Backend Module.

Provides unified interface for document storage across different backends:
- Local file system storage
- AWS S3 storage (with LocalStack support)

Usage:
    from storage_backend import create_storage

    storage = create_storage(config)
    storage.upload_file(file_stream, "document.pdf")
"""

from storage_backend.factory import create_storage

__all__ = ["create_storage"]
