"""
Upload router.

Route definitions for file upload endpoints.
"""

from typing import Union

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from app.api.models import UploadResponse, ErrorResponse
from app.modules.upload import UploadService
from app.api.dependencies import get_upload_service
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["upload"])


@router.post("/upload", response_model=Union[UploadResponse, ErrorResponse])
async def upload_file(
    file: UploadFile = File(...),
    service: UploadService = Depends(get_upload_service)
):
    """
    Upload a document file.
    
    Args:
        file: Uploaded file (multipart/form-data)
        service: Upload service (injected)
    
    Returns:
        UploadResponse: Upload result with file metadata
    """
    content = await _read_file_content(file)
    
    try:
        return service.upload_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=str(e),
                error_code="VALIDATION_ERROR"
            ).model_dump()
        )
    except Exception as e:
        logger.error(codes.API_UPLOAD_FAILED, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=codes.MSG_API_UPLOAD_FAILED,
                error_code="UPLOAD_ERROR"
            ).model_dump()
        )


async def _read_file_content(file: UploadFile) -> bytes:
    """
    Read file content from upload.
    
    Args:
        file: Uploaded file
        
    Returns:
        bytes: File content
        
    Raises:
        HTTPException: If read fails
    """
    try:
        return await file.read()
    except Exception as e:
        logger.error(codes.API_UPLOAD_FAILED, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=codes.MSG_API_UPLOAD_FAILED,
                error_code="READ_ERROR"
            ).model_dump()
        )

