"""
FastAPI application for RAG document upload.

Main application entry point with middleware and router configuration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.routers import health, upload, files, query
from config import Config
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)


def get_config() -> Config:
    """
    Get the singleton Config instance (lazy initialization).
    
    This function ensures Config is only instantiated when actually needed,
    not at module import time.
    """
    return Config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    config = get_config()
    logger.info(
        codes.API_SERVER_STARTING,
        host=config.api.host,
        port=config.api.port,
        storage_backend=config.storage.backend
    )
    
    logger.info(codes.API_SERVER_STARTED, message=codes.MSG_API_SERVER_STARTED)
    
    yield
    
    # Shutdown
    logger.info(codes.API_SERVER_SHUTDOWN, message=codes.MSG_API_SERVER_SHUTDOWN)


# Create FastAPI application
app = FastAPI(
    title="RAG Application API",
    description="API for document management and RAG query operations",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_config().api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(files.router)
app.include_router(query.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Logs the error and returns a generic error response.
    
    Args:
        request: FastAPI request
        exc: Exception that was raised
    
    Returns:
        JSONResponse: Error response
    """
    logger.error(
        codes.API_ERROR,
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": codes.MSG_API_ERROR,
            "error_code": "INTERNAL_ERROR"
        }
    )


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        dict: API welcome message and version
    """
    return {
        "name": "RAG Application API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "upload": "/api/v1/upload",
            "files": "/api/v1/files",
            "query": "/api/v1/query"
        }
    }


@app.get("/favicon.ico")
async def favicon():
    """
    Return empty response for favicon to avoid 404 in logs.
    
    Browsers automatically request /favicon.ico. Returning 204 No Content
    prevents 404 errors from cluttering logs.
    
    Returns:
        Response: Empty 204 No Content response
    """
    return Response(status_code=204)

