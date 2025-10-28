"""
FastAPI Application for RAG Document Upload.

Provides streaming file upload endpoints with support for:
- Standard multipart uploads
- Chunked streaming uploads
- Direct S3/local storage integration
"""

from api.main import app

__all__ = ["app"]
