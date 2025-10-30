"""
FastAPI application for RAG document upload.

Main application entry point with middleware and router configuration.
Embeds Streamlit UI for unified application architecture.
"""

import atexit
import os
import signal
import subprocess
import sys
from typing import Optional

import constants
import trace.codes as codes
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from app.routers import files, health, query, upload
from config import Config
from logger import get_logger

logger = get_logger(__name__)

# Global process handle for Streamlit
streamlit_process: Optional[subprocess.Popen] = None


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


def start_streamlit_ui() -> None:
    """
    Start Streamlit UI server as a subprocess.

    Raises:
        RuntimeError: If Streamlit fails to start
    """
    global streamlit_process

    config = get_config()

    if not config.ui.enabled:
        logger.info(codes.UI_STREAMLIT_NOT_INSTALLED, message="UI disabled in configuration")
        return

    logger.info(codes.UI_STREAMLIT_STARTING)

    try:
        # Check if streamlit is installed using the same Python interpreter
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            logger.warning(
                codes.UI_STREAMLIT_NOT_INSTALLED,
                message=constants.UI_STREAMLIT_NOT_INSTALLED,
                hint=constants.UI_STREAMLIT_INSTALL_HINT,
            )
            return

    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning(
            codes.UI_STREAMLIT_NOT_INSTALLED,
            message=constants.UI_STREAMLIT_NOT_INSTALLED,
            hint=constants.UI_STREAMLIT_INSTALL_HINT,
        )
        return

    try:
        # Start Streamlit as subprocess using the same Python interpreter
        streamlit_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app/ui/main.py",
                "--server.port",
                str(config.ui.port),
                "--server.headless",
                str(config.ui.headless).lower(),
                "--server.enableCORS",
                str(config.ui.enable_cors).lower(),
                "--server.enableXsrfProtection",
                str(config.ui.enable_xsrf_protection).lower(),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        logger.info(
            codes.UI_STREAMLIT_STARTED,
            port=config.ui.port,
            host=config.ui.host,
        )

    except Exception as e:
        logger.error(
            codes.UI_STREAMLIT_FAILED,
            error=str(e),
            message=constants.UI_STREAMLIT_STARTUP_FAILED,
            exc_info=True,
        )
        raise RuntimeError(constants.UI_STREAMLIT_STARTUP_FAILED) from e


def stop_streamlit_ui() -> None:
    """Stop Streamlit UI server gracefully."""
    global streamlit_process

    if streamlit_process is None:
        return

    config = get_config()
    logger.info(codes.UI_STREAMLIT_STOPPING)

    try:
        # Try graceful shutdown first
        streamlit_process.terminate()
        streamlit_process.wait(timeout=config.ui.shutdown_timeout)
        logger.info(codes.UI_STREAMLIT_STOPPED)

    except subprocess.TimeoutExpired:
        # Force kill if graceful shutdown fails
        logger.warning(
            codes.UI_STREAMLIT_FAILED,
            message="Graceful shutdown timeout, forcing termination",
        )
        streamlit_process.kill()
        streamlit_process.wait()
        logger.info(codes.UI_STREAMLIT_STOPPED, message="Forced termination")

    except Exception as e:
        logger.error(
            codes.UI_STREAMLIT_FAILED,
            error=str(e),
            message=constants.UI_STREAMLIT_SHUTDOWN_FAILED,
            exc_info=True,
        )

    finally:
        streamlit_process = None


def cleanup_streamlit() -> None:
    """Cleanup function for atexit - ensures Streamlit is stopped."""
    if streamlit_process is not None:
        stop_streamlit_ui()


# Register cleanup handler
atexit.register(cleanup_streamlit)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events including Streamlit UI.
    """
    # Startup
    config = get_config()
    logger.info(
        codes.API_SERVER_STARTING,
        host=config.api.host,
        port=config.api.port,
        storage_backend=config.storage.backend,
        ui_enabled=config.ui.enabled,
    )

    # Start Streamlit UI
    start_streamlit_ui()

    # Log all registered routes
    log_registered_routes(app)

    logger.info(codes.API_SERVER_STARTED, message=codes.MSG_API_SERVER_STARTED)

    yield

    # Shutdown
    logger.info(codes.API_SERVER_SHUTDOWN, message=codes.MSG_API_SERVER_SHUTDOWN)

    # Stop Streamlit UI
    stop_streamlit_ui()


# Create FastAPI application
app = FastAPI(
    title="RAG Application API",
    description="API for document management and RAG query operations",
    version="1.0.0",
    lifespan=lifespan,
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


@app.get(constants.UI_ROUTE_ROOT, response_class=RedirectResponse)
async def root():
    """
    Root endpoint - redirects to API documentation.

    Returns:
        RedirectResponse: Redirects to /docs
    """
    return RedirectResponse(url=constants.UI_ROUTE_DOCS)


@app.get(constants.UI_ROUTE_LANGCHAIN_CHAT, response_class=HTMLResponse)
async def langchain_chat():
    """
    LangChain RAG chat UI endpoint.

    Serves the Streamlit UI in an iframe for unified application architecture.

    Returns:
        HTMLResponse: HTML page with embedded Streamlit iframe
    """
    config = get_config()

    logger.info(codes.UI_LANGCHAIN_CHAT_ACCESSED)

    if not config.ui.enabled or streamlit_process is None:
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{constants.UI_IFRAME_TITLE_LANGCHAIN}</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background: #f5f5f5;
                    }}
                    .message {{
                        text-align: center;
                        padding: 2rem;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }}
                </style>
            </head>
            <body>
                <div class="message">
                    <h2>⚠️ UI Not Available</h2>
                    <p>{constants.UI_STREAMLIT_NOT_INSTALLED}</p>
                    <p><code>{constants.UI_STREAMLIT_INSTALL_HINT}</code></p>
                </div>
            </body>
            </html>
            """,
            status_code=503,
        )

    streamlit_url = f"http://{config.ui.host}:{config.ui.port}"

    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{constants.UI_IFRAME_TITLE_LANGCHAIN}</title>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    overflow: hidden;
                }}
                iframe {{
                    width: 100%;
                    height: 100vh;
                    border: none;
                }}
            </style>
        </head>
        <body>
            <iframe src="{streamlit_url}" allowfullscreen></iframe>
        </body>
        </html>
        """
    )


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
