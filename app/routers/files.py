"""
Files router.

Route definitions for file management endpoints.
"""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.files.response import FileListResponse, FileMetadataResponse
from app.api.models.common import ErrorResponse
from app.modules.files import FileManagementService
from app.api.dependencies import get_file_service
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["files"])


@router.get("/files", response_model=Union[FileListResponse, ErrorResponse])
async def list_files(service: FileManagementService = Depends(get_file_service)):
    """
    List all uploaded files.
    
    Args:
        service: File service (injected)
    
    Returns:
        FileListResponse: List of files with count
    """
    try:
        return service.list_files()
    except Exception as e:
        logger.error(codes.API_ERROR, operation="list_files", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=codes.MSG_API_ERROR,
                error_code="LIST_ERROR"
            ).model_dump()
        )


@router.get("/files/{filename}", response_model=Union[FileMetadataResponse, ErrorResponse])
async def get_file_metadata(
    filename: str,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Get metadata for a specific file.
    
    Args:
        filename: Name of the file
        service: File service (injected)
    
    Returns:
        FileMetadataResponse: File metadata
    """
    try:
        return service.get_file_metadata(filename)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error=codes.MSG_API_FILE_NOT_FOUND,
                error_code="FILE_NOT_FOUND"
            ).model_dump()
        )
    except Exception as e:
        logger.error(codes.API_ERROR, operation="get_metadata", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=codes.MSG_API_ERROR,
                error_code="METADATA_ERROR"
            ).model_dump()
        )


@router.delete("/files/{filename}", response_model=dict)
async def delete_file(
    filename: str,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Delete a file from storage.
    
    Args:
        filename: Name of the file to delete
        service: File service (injected)
    
    Returns:
        dict: Success message with filename
    """
    try:
        return service.delete_file(filename)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error=codes.MSG_API_FILE_NOT_FOUND,
                error_code="FILE_NOT_FOUND"
            ).model_dump()
        )
    except Exception as e:
        logger.error(codes.API_ERROR, operation="delete_file", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=codes.MSG_API_ERROR,
                error_code="DELETE_ERROR"
            ).model_dump()
        )

