"""
Rate limiting dependencies for FastAPI.

Provides decorators and dependencies for applying rate limits to routes.
"""

from functools import wraps
from typing import Callable, Optional

from fastapi import HTTPException, Request, status

from app.modules.auth.dependencies import get_current_user_optional
from app.modules.ratelimit.enums import RateLimitKeyStrategy
from app.modules.ratelimit.service import RateLimitService
from logger import get_logger

logger = get_logger(__name__)

# Global rate limit service instance
_rate_limit_service: RateLimitService = None


def get_rate_limit_service() -> RateLimitService:
    """Get or create rate limit service instance (singleton)."""
    global _rate_limit_service

    if _rate_limit_service is None:
        _rate_limit_service = RateLimitService()

    return _rate_limit_service


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.

    Handles proxy headers (X-Forwarded-For) correctly.

    Args:
        request: FastAPI request

    Returns:
        Client IP address
    """
    # Try X-Forwarded-For header first (for proxies)
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        # Take first IP in chain
        return forwarded_for.split(",")[0].strip()

    # Fall back to direct client IP
    if request.client:
        return request.client.host

    return "unknown"


def get_session_id(request: Request) -> Optional[str]:
    """
    Extract session ID from request.

    Tries cookie first, then Authorization header.

    Args:
        request: FastAPI request

    Returns:
        Session ID or None
    """
    # Try session cookie
    session_id = request.cookies.get("session_id")
    if session_id:
        return session_id

    # Try Authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Use token as session ID
        return auth_header.split(" ")[1][:50]  # Truncate for key size

    return None


async def build_rate_limit_key(
    request: Request,
    route_name: str,
    strategy: str = RateLimitKeyStrategy.IP,
) -> str:
    """
    Build rate limit key based on strategy.

    Args:
        request: FastAPI request
        route_name: Route name
        strategy: Key strategy (ip, user, session, route, ip_and_route, user_and_route)

    Returns:
        Rate limit key
    """
    strategy = RateLimitKeyStrategy(strategy)

    if strategy == RateLimitKeyStrategy.IP:
        return get_client_ip(request)

    elif strategy == RateLimitKeyStrategy.USER:
        # Get authenticated user ID
        user = await get_current_user_optional(request)
        if user:
            return f"user:{user.id}"
        # Fall back to IP if not authenticated
        return get_client_ip(request)

    elif strategy == RateLimitKeyStrategy.SESSION:
        # Get session ID
        session_id = get_session_id(request)
        if session_id:
            return f"session:{session_id}"
        # Fall back to IP if no session
        return get_client_ip(request)

    elif strategy == RateLimitKeyStrategy.ROUTE:
        # Route-only limiting (global per route)
        return f"route:{route_name}"

    elif strategy == RateLimitKeyStrategy.IP_AND_ROUTE:
        ip = get_client_ip(request)
        return f"{ip}:route:{route_name}"

    elif strategy == RateLimitKeyStrategy.USER_AND_ROUTE:
        user = await get_current_user_optional(request)
        if user:
            return f"user:{user.id}:route:{route_name}"
        # Fall back to IP + route if not authenticated
        ip = get_client_ip(request)
        return f"{ip}:route:{route_name}"

    # Default to IP
    return get_client_ip(request)


async def check_rate_limit(
    route_name: str,
    request: Request,
    rate_limit_service: RateLimitService = None,
) -> None:
    """
    Check rate limit for request.

    Gets rate limit config (including key_strategy), builds appropriate key,
    and checks against limit.

    Args:
        route_name: Route name for rate limit config
        request: FastAPI request
        rate_limit_service: Rate limit service (optional)

    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    service = rate_limit_service or get_rate_limit_service()

    # Get route config (including key_strategy)
    route_config = service.get_route_config_with_strategy(route_name)
    key_strategy = route_config.get("key_strategy", RateLimitKeyStrategy.IP)

    # Build rate limit key based on strategy
    client_id = await build_rate_limit_key(request, route_name, key_strategy)

    # Check rate limit
    is_allowed, headers_info = service.check_rate_limit(route_name, client_id)

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "route": route_name,
                "limit": headers_info.get("limit"),
                "window": headers_info.get("window"),
                "message": f"Too many requests. Try again in {headers_info.get('window')} seconds.",
            },
            headers={
                "X-RateLimit-Limit": str(headers_info.get("limit", 0)),
                "X-RateLimit-Remaining": str(headers_info.get("remaining", 0)),
                "X-RateLimit-Window": str(headers_info.get("window", 0)),
                "Retry-After": str(headers_info.get("window", 60)),
            },
        )


def rate_limit(route_name: str):
    """
    Decorator for applying rate limit to route.

    Usage:
        @router.post("/api/v1/auth/login")
        @rate_limit("auth_login")
        async def login(request: Request, ...):
            pass

    Args:
        route_name: Route name matching config

    Returns:
        Decorator function
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None:
                request = kwargs.get("request")

            if request:
                await check_rate_limit(route_name, request)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class RateLimitDependency:
    """
    Dependency class for rate limiting.

    Usage:
        from app.modules.ratelimit.dependencies import RateLimitDependency

        @router.post("/login", dependencies=[Depends(RateLimitDependency("auth_login"))])
        async def login(...):
            pass
    """

    def __init__(self, route_name: str):
        """
        Initialize rate limit dependency.

        Args:
            route_name: Route name matching config
        """
        self.route_name = route_name

    async def __call__(self, request: Request):
        """
        Check rate limit.

        Args:
            request: FastAPI request

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        await check_rate_limit(self.route_name, request)

