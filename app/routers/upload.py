"""
Upload router.

Route definitions for file upload endpoints.
"""

from typing import Union, List, Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

import constants
from app.modules.upload.response import UploadResponse, BatchUploadResponse, FileUploadResult
from app.api.models.common import ErrorResponse
from app.modules.upload import UploadService
from app.api.dependencies import get_upload_service
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["upload"])


@router.post("/upload", response_model=Union[UploadResponse, BatchUploadResponse, ErrorResponse])
async def upload(
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    service: UploadService = Depends(get_upload_service)
):
    """
    Upload single or multiple document files.
    
    Supports both:
    - Single file upload: field name 'file'
    - Batch upload: field name 'files'
    
    Args:
        file: Single uploaded file (optional)
        files: Multiple uploaded files (optional)
        service: Upload service (injected)
    
    Returns:
        UploadResponse: For single file upload
        BatchUploadResponse: For multiple files upload
    """
    _validate_upload_request(file, files)
    
    if file:
        return await _handle_single_file_upload(file, service)
    
    if files:
        return await _handle_batch_upload(files, service)
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorResponse(
            error=constants.ERROR_UPLOAD_NO_FILE_OR_FILES,
            error_code=constants.ERROR_CODE_NO_FILES
        ).model_dump()
    )


def _validate_upload_request(
    file: Optional[UploadFile],
    files: Optional[List[UploadFile]]
) -> None:
    """
    Validate upload request parameters.
    
    Args:
        file: Single file parameter (optional)
        files: Multiple files parameter (optional)
        
    Raises:
        HTTPException: If both parameters are provided
    """
    if file and files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=constants.ERROR_UPLOAD_BOTH_FIELDS,
                error_code=constants.ERROR_CODE_INVALID_REQUEST
            ).model_dump()
        )


async def _handle_single_file_upload(
    file: UploadFile,
    service: UploadService
) -> UploadResponse:
    """
    Handle single file upload.
    
    Args:
        file: Uploaded file
        service: Upload service
        
    Returns:
        UploadResponse: Upload result
    """
    content = await _read_file_content(file)
    
    try:
        return service.upload_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=str(e),
                error_code=constants.ERROR_CODE_VALIDATION_ERROR
            ).model_dump()
        )
    except Exception as e:
        logger.error(codes.API_UPLOAD_FAILED, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=codes.MSG_API_UPLOAD_FAILED,
                error_code=constants.ERROR_CODE_UPLOAD_ERROR
            ).model_dump()
        )


async def _handle_batch_upload(
    files: List[UploadFile],
    service: UploadService
) -> BatchUploadResponse:
    """
    Handle batch file upload.
    
    Args:
        files: List of uploaded files
        service: Upload service
        
    Returns:
        BatchUploadResponse: Batch upload results
    """
    results = []
    successful = 0
    failed = 0
    
    for uploaded_file in files:
        result = await _process_single_file_in_batch(uploaded_file, service)
        results.append(result)
        
        if result.success:
            successful += 1
        else:
            failed += 1
    
    return BatchUploadResponse(
        total=len(files),
        successful=successful,
        failed=failed,
        results=results
    )


async def _process_single_file_in_batch(
    file: UploadFile,
    service: UploadService
) -> FileUploadResult:
    """
    Process single file in batch upload.
    
    Args:
        file: Uploaded file
        service: Upload service
        
    Returns:
        FileUploadResult: Result for this file
    """
    try:
        content = await _read_file_content(file)
        upload_result = service.upload_file(file.filename, content)
        
        return FileUploadResult(
            filename=file.filename,
            success=True,
            file_id=upload_result.file_id,
            path=upload_result.path,
            size=upload_result.size,
            file_type=upload_result.file_type,
            checksum=upload_result.checksum,
            backend=upload_result.backend,
            indexed=upload_result.indexed
        )
    except ValueError as e:
        logger.warning(codes.API_UPLOAD_FAILED, filename=file.filename, error=str(e))
        return FileUploadResult(
            filename=file.filename,
            success=False,
            error=str(e),
            error_code=constants.ERROR_CODE_VALIDATION_ERROR
        )
    except Exception as e:
        logger.error(codes.API_UPLOAD_FAILED, filename=file.filename, error=str(e), exc_info=True)
        return FileUploadResult(
            filename=file.filename,
            success=False,
            error=constants.ERROR_UPLOAD_FAILED,
            error_code=constants.ERROR_CODE_UPLOAD_ERROR
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
                error=constants.ERROR_UPLOAD_READ_FAILED,
                error_code=constants.ERROR_CODE_READ_ERROR
            ).model_dump()
        )

