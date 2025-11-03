"""
Rate Limiting Middleware.

Applies rate limiting to all incoming requests before authentication.
Order: Rate Limit → Authentication → RBAC
"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import trace.codes as codes
from app.modules.ratelimit.dependencies import build_rate_limit_key
from app.modules.ratelimit.service import RateLimitService
from logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware that applies to all requests.

    This middleware runs BEFORE authentication, checking rate limits based on
    configured strategy (IP, user, session, route, etc.).
    """

    def __init__(self, app):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application instance
        """
        super().__init__(app)
        self.rate_limit_service = RateLimitService()
        logger.info(codes.RATE_LIMIT_MIDDLEWARE_INITIALIZED)

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response with rate limit headers
        """
        # Skip rate limiting for health check and static assets
        if request.url.path in ["/api/v1/health", "/favicon.ico"] or request.url.path.startswith("/static/"):
            return await call_next(request)

        # Determine route name from path and method
        route_name = self._get_route_name(request)

        # Get rate limit configuration for this route
        route_config = self.rate_limit_service.get_route_config_with_strategy(
            route_name
        )

        if not route_config.get("enabled", True):
            # Rate limiting disabled for this route
            return await call_next(request)

        # Build rate limit key based on strategy
        key_strategy = route_config.get("key_strategy", "ip")
        client_id = await build_rate_limit_key(request, route_name, key_strategy)

        # Check rate limit
        is_allowed, headers_info = self.rate_limit_service.check_rate_limit(
            route_name, client_id
        )

        if not is_allowed:
            # Rate limit exceeded
            reset_time = int(time.time()) + headers_info.get("window", 60)
            
            logger.warning(
                codes.RATE_LIMIT_EXCEEDED,
                route=route_name,
                client_id=client_id,
                limit=headers_info["limit"],
                remaining=0,
            )

            # Return 429 Too Many Requests
            response = Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(headers_info["limit"])
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            response.headers["Retry-After"] = str(headers_info.get("window", 60))

            return response

        # Rate limit passed, proceed with request
        response = await call_next(request)

        # Add rate limit headers to successful response
        reset_time = int(time.time()) + headers_info.get("window", 60)
        response.headers["X-RateLimit-Limit"] = str(headers_info.get("limit", ""))
        response.headers["X-RateLimit-Remaining"] = str(headers_info.get("remaining", ""))
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_route_name(self, request: Request) -> str:
        """
        Extract route name from request.

        Args:
            request: FastAPI request

        Returns:
            Route name for rate limit lookup
        """
        # Try to get route name from FastAPI route
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "name") and route.name:
                return route.name

        # Fallback: use path + method
        path = request.url.path
        method = request.method

        # Map common paths to route names
        if path.startswith("/api/v1/auth/"):
            return f"auth_{path.split('/')[-1]}"
        elif path.startswith("/api/v1/admin/"):
            parts = path.split("/")
            if len(parts) >= 5:
                resource = parts[4]  # e.g., 'users', 'roles'
                return f"admin_{resource}"
        elif path.startswith("/api/v1/"):
            parts = path.split("/")
            if len(parts) >= 4:
                return parts[3]  # e.g., 'upload', 'files'

        # Default: use path as route name
        return path.replace("/", "_").strip("_")

