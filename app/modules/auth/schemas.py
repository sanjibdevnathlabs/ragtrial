"""
Authentication request/response schemas.

Pydantic models for API validation.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Registration schemas
class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, description="Password")


class RegisterResponse(BaseModel):
    """User registration response."""

    user_id: str = Field(..., description="Created user ID")
    email: str = Field(..., description="User email")
    message: str = Field(..., description="Success message")


# Login schemas
class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration (seconds)")
    user: Optional[dict] = Field(None, description="User information (included on login)")


# Token refresh schemas
class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class AccessTokenResponse(BaseModel):
    """Access token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Expiration time (seconds)")


# Logout schemas
class LogoutRequest(BaseModel):
    """Logout request."""

    refresh_token: str = Field(..., description="JWT refresh token to revoke")


class LogoutResponse(BaseModel):
    """Logout response."""

    message: str = Field(..., description="Success message")


# Password change schemas
class ChangePasswordRequest(BaseModel):
    """Change password request."""

    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordChangeResponse(BaseModel):
    """Password change response."""

    message: str = Field(..., description="Success message")


# Password reset schemas
class PasswordResetRequest(BaseModel):
    """Password reset request."""

    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""

    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordResetResponse(BaseModel):
    """Password reset response."""

    message: str = Field(..., description="Success message")


# Email verification schemas
class EmailVerificationRequest(BaseModel):
    """Email verification request."""

    token: str = Field(..., description="Verification token from email")


class EmailVerificationResponse(BaseModel):
    """Email verification response."""

    message: str = Field(..., description="Success message")


# User info schemas
class UserResponse(BaseModel):
    """User information response."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    is_verified: bool = Field(..., description="Email verified")
    is_active: bool = Field(..., description="Account active")
    has_password: bool = Field(..., description="Has password set")
    created_at: int = Field(..., description="Creation timestamp (ms)")
    permissions: list[str] = Field(default_factory=list, description="User permissions")


# Error response
class ErrorResponse(BaseModel):
    """Error response."""

    detail: str = Field(..., description="Error message")

