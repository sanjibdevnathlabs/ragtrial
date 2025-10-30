"""
FastAPI application for RAG document upload.

Main application entry point with middleware and router configuration.
"""

import trace.codes as codes
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

import constants
from app.routers import devdocs, files, health, query, upload
from config import Config
from logger import get_logger

logger = get_logger(__name__)


def get_config() -> Config:
    """
    Get the singleton Config instance (lazy initialization).

    This function ensures Config is only instantiated when actually needed,
    not at module import time.
    """
    return Config()


def log_registered_routes(app: FastAPI):
    """
    Display all registered routes in a formatted table.

    Args:
        app: FastAPI application instance
    """
    # Collect routes grouped by path
    routes_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            # Skip HEAD and OPTIONS methods (auto-generated)
            methods = [m for m in route.methods if m not in ["HEAD", "OPTIONS"]]
            if methods:
                route_name = getattr(route, "name", "")
                routes_info.append(
                    {"methods": sorted(methods), "path": route.path, "name": route_name}
                )

    # Sort by path for better readability
    routes_info.sort(key=lambda x: x["path"])

    # Calculate column widths
    max_method_len = max(len(", ".join(r["methods"])) for r in routes_info)
    max_path_len = max(len(r["path"]) for r in routes_info)
    max_name_len = max(len(r["name"]) for r in routes_info)

    # Ensure minimum widths
    method_width = max(max_method_len, 10)
    path_width = max(max_path_len, 30)
    name_width = max(max_name_len, 20)

    # Print table header
    print("\n" + "=" * 80)
    print("🚀 REGISTERED API ROUTES")
    print("=" * 80)

    # Print column headers
    header = (
        f"{'METHOD':<{method_width}} | {'PATH':<{path_width}} | {'NAME':<{name_width}}"
    )
    print(header)
    print("-" * len(header))

    # Print each route
    for route_data in routes_info:
        methods_str = ", ".join(route_data["methods"])
        path = route_data["path"]
        name = route_data["name"]
        print(
            f"{methods_str:<{method_width}} | {path:<{path_width}} | "
            f"{name:<{name_width}}"
        )

    # Print footer
    print("=" * 80)
    print(f"Total routes: {len(routes_info)}")
    print("=" * 80 + "\n")


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
        storage_backend=config.storage.backend,
    )

    # Log all registered routes
    log_registered_routes(app)

    logger.info(codes.API_SERVER_STARTED, message=codes.MSG_API_SERVER_STARTED)

    yield

    # Shutdown
    logger.info(codes.API_SERVER_SHUTDOWN, message=codes.MSG_API_SERVER_SHUTDOWN)


# Create FastAPI application
app = FastAPI(
    title="RAG Application API",
    description="API for document management and RAG query operations",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Disable default docs (using React-rendered Swagger UI)
    redoc_url=None,  # Disable redoc
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
app.include_router(devdocs.router)

# Mount static files for React frontend
# This serves the built React app (CSS, JS, assets)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


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
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": codes.MSG_API_ERROR,
            "error_code": "INTERNAL_ERROR",
        },
    )


@app.get(constants.UI_ROUTE_ROOT, response_class=FileResponse)
async def root():
    """
    Root endpoint - serves React landing page.

    Returns:
        FileResponse: The React app's index.html
    """
    return FileResponse("app/static/dist/index.html")


# Removed: /docs and /langchain/chat now handled by React Router
# See serve_react_routes() below


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


# Catch-all for React Router - serve index.html for frontend routes
# Use specific paths instead of greedy {full_path:path} to avoid catching API routes
@app.get("/about", response_class=FileResponse)
@app.get("/dev-docs", response_class=FileResponse)
@app.get("/docs", response_class=FileResponse)
@app.get("/langchain/chat", response_class=FileResponse)
async def serve_react_routes():
    """
    Serve React app for client-side routes.

    All these routes are handled by React Router on the client side:
    - /about: About page
    - /dev-docs: Developer documentation
    - /docs: API documentation (Swagger UI in iframe)
    - /langchain/chat: Chat UI (Streamlit in iframe)

    We serve index.html which loads the React app, and React Router
    handles the navigation. This ensures consistent navbar across all pages.

    Returns:
        FileResponse: The React app's index.html
    """
    return FileResponse("app/static/dist/index.html")
