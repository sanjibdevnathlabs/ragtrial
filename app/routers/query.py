"""
Query router for RAG query endpoints.

Provides HTTP endpoints for querying the RAG system.
"""

import trace.codes as codes

from fastapi import APIRouter, HTTPException, status

import constants
from app.api.models.common import ErrorResponse
from app.modules.query import QueryService
from app.modules.query.request import QueryRequest
from app.modules.query.response import QueryResponse, SourceDocument
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/query",
    tags=["query"],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query RAG System",
    description="Ask a question and get an answer from the RAG system with source documents",
)
async def query_rag(request: QueryRequest) -> QueryResponse:
    """
    Process a query through the RAG system.

    Args:
        request: Query request with question

    Returns:
        QueryResponse with answer and sources

    Raises:
        HTTPException: If query processing fails
    """
    try:
        service = QueryService()
        result = service.query(request.question)

        sources = []
        for idx, source in enumerate(result.get(constants.RESPONSE_KEY_SOURCES, [])):
            metadata = source.get("metadata", {})
            source_path = metadata.get(constants.META_SOURCE, "unknown")

            from pathlib import Path

            filename = Path(source_path).name if source_path != "unknown" else "unknown"

            sources.append(
                SourceDocument(
                    filename=filename,
                    chunk_index=idx,
                    content=source.get("content", ""),
                )
            )

        return QueryResponse(
            success=True,
            answer=result.get(constants.RESPONSE_KEY_ANSWER, ""),
            sources=sources,
            has_answer=result.get(constants.RESPONSE_KEY_HAS_ANSWER, False),
            query=request.question,
        )

    except RuntimeError as e:
        logger.error(codes.QUERY_API_FAILED, error=str(e), error_type="RuntimeError")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except ValueError as e:
        logger.error(codes.QUERY_API_FAILED, error=str(e), error_type="ValueError")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        logger.error(
            codes.QUERY_API_FAILED,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_QUERY_PROCESSING_FAILED,
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Query System Health",
    description="Check if the RAG query system is ready to process queries",
)
async def query_health() -> dict:
    """
    Check query system health.

    Returns:
        Health status information
    """
    try:
        service = QueryService()
        health_info = service.health_check()

        return {"status": "healthy", "rag_system": health_info}

    except Exception as e:
        logger.error(
            codes.OPERATION_FAILED,
            operation="query_health_check",
            error=str(e),
            exc_info=True,
        )
        return {"status": "unhealthy", "error": str(e)}
