"""
FastAPI Application for RAG Document Upload.

Provides streaming file upload endpoints with support for:
- Standard multipart uploads
- Chunked streaming uploads
- Direct S3/local storage integration

To run the API server:
    uvicorn app.api.main:app --reload
    
Or import directly:
    from app.api.main import app
"""

# Empty __init__.py to avoid circular imports
# Import app.api.main directly when needed
