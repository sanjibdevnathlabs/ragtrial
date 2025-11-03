"""
Authentication dependencies for FastAPI.

Provides JWT authentication middleware and current user extraction.
"""

from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.auth.service import AuthService
from logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """Get AuthService instance."""
    return AuthService()


async def get_current_user_optional(request, auth_service: AuthService = None) -> Optional[Dict]:
    """
    Extract current user from JWT token (optional).

    Returns None if no token present or invalid.
    Used for rate limiting fallback strategies.

    Args:
        request: FastAPI Request object
        auth_service: Auth service instance

    Returns:
        User dictionary or None
    """
    if auth_service is None:
        auth_service = get_auth_service()

    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            user = auth_service.verify_token(token)
            return user
        return None
    except Exception:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict:
    """
    Extract current user from JWT token.

    Args:
        credentials: HTTP Bearer credentials
        auth_service: Auth service instance

    Returns:
        User dictionary

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    user = auth_service.verify_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Dict = Depends(get_current_user),
) -> Dict:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        User dictionary

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    return current_user


async def get_current_verified_user(
    current_user: Dict = Depends(get_current_active_user),
) -> Dict:
    """
    Get current verified user.

    Args:
        current_user: Current active user

    Returns:
        User dictionary

    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )

    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[Dict]:
    """
    Extract current user from token (optional).

    Returns None if no token provided or token invalid.

    Args:
        credentials: HTTP Bearer credentials (optional)
        auth_service: Auth service instance

    Returns:
        User dictionary or None
    """
    if not credentials:
        return None

    token = credentials.credentials
    user = auth_service.verify_token(token)

    return user

