"""
Authentication router.

Handles user registration, login, logout, password operations.
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.modules.auth.dependencies import get_current_active_user
from app.modules.ratelimit.dependencies import RateLimitDependency
from app.modules.auth.schemas import (
    AccessTokenResponse,
    ChangePasswordRequest,
    EmailVerificationRequest,
    EmailVerificationResponse,
    ErrorResponse,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    PasswordChangeResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService
from app.modules.password.service import PasswordService
from app.modules.registration.service import RegistrationService
from app.modules.verification.service import VerificationService
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def get_client_metadata(request: Request) -> Dict:
    """Extract client metadata from request."""
    return {
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None,
    }


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
    dependencies=[Depends(RateLimitDependency("auth_register"))],
)
async def register(data: RegisterRequest):
    """
    Register new user account.

    Creates a new user and sends verification email.
    """
    registration_service = RegistrationService()

    user, error = registration_service.register_user(
        data.email, data.full_name, data.password
    )

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return RegisterResponse(
        user_id=user["id"],
        email=user["email"],
        message="Registration successful. Please check your email to verify your account.",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
    dependencies=[Depends(RateLimitDependency("auth_login"))],
)
async def login(data: LoginRequest, request: Request):
    """
    Login with email and password.

    Returns JWT access and refresh tokens with user information.
    """
    from app.modules.user.service import UserService
    from app.modules.rbac.core import PermissionService
    
    auth_service = AuthService()
    client_metadata = get_client_metadata(request)

    tokens, error = auth_service.login(data.email, data.password, client_metadata)

    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    # Get user info with permissions
    user_service = UserService()
    user = user_service.get_by_email(data.email)
    
    if user:
        permission_service = PermissionService()
        permissions = permission_service.get_all_user_permissions(user["id"])
        user["permissions"] = permissions

    return TokenResponse(**tokens, user=user)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    responses={401: {"model": ErrorResponse}},
)
async def refresh_token(data: RefreshTokenRequest):
    """
    Refresh access token.

    Uses refresh token to generate new access token.
    """
    auth_service = AuthService()

    tokens, error = auth_service.refresh_token(data.refresh_token)

    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    return AccessTokenResponse(**tokens)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={401: {"model": ErrorResponse}},
)
async def logout(data: LogoutRequest):
    """
    Logout from current session.

    Revokes the provided refresh token.
    """
    auth_service = AuthService()

    success, error = auth_service.logout(data.refresh_token)

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return LogoutResponse(message="Logout successful")


@router.post(
    "/logout-all",
    response_model=LogoutResponse,
    responses={401: {"model": ErrorResponse}},
    dependencies=[Depends(get_current_active_user)],
)
async def logout_all(current_user: Dict = Depends(get_current_active_user)):
    """
    Logout from all sessions.

    Revokes all refresh tokens for the current user.
    Requires valid access token.
    """
    auth_service = AuthService()

    count, error = auth_service.logout_all(current_user["id"])

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return LogoutResponse(message=f"Logged out from {count} session(s)")


@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}},
)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_active_user),
):
    """
    Get current user information with permissions.

    Requires valid access token.
    Returns user data with all effective permissions.
    """
    from app.modules.rbac.core import PermissionService
    
    # Get user permissions
    permission_service = PermissionService()
    permissions = permission_service.get_all_user_permissions(current_user["id"])
    
    # Add permissions to user data
    user_data = {**current_user, "permissions": permissions}
    
    return UserResponse(**user_data)


@router.post(
    "/password/change",
    response_model=PasswordChangeResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
    dependencies=[Depends(RateLimitDependency("auth_password_change"))],
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: Dict = Depends(get_current_active_user),
):
    """
    Change password.

    Requires old password verification and valid access token.
    """
    password_service = PasswordService()

    success, error = password_service.change_password(
        current_user["id"], data.old_password, data.new_password
    )

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return PasswordChangeResponse(message="Password changed successfully")


@router.post(
    "/password/reset/request",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    responses={429: {"model": ErrorResponse}},
    dependencies=[Depends(RateLimitDependency("auth_password_reset_request"))],
)
async def request_password_reset(data: PasswordResetRequest):
    """
    Request password reset.

    Sends password reset email with token.
    Always returns success (doesn't reveal if email exists).
    """
    password_service = PasswordService()

    password_service.request_reset(data.email)

    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent."
    )


@router.post(
    "/password/reset/confirm",
    response_model=PasswordResetResponse,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
    dependencies=[Depends(RateLimitDependency("auth_password_reset_confirm"))],
)
async def confirm_password_reset(data: PasswordResetConfirm):
    """
    Confirm password reset with token.

    Resets password using token from email.
    """
    password_service = PasswordService()

    success, error = password_service.reset_with_token(data.token, data.new_password)

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return PasswordResetResponse(message="Password reset successful")


@router.post(
    "/verify/email",
    response_model=EmailVerificationResponse,
    responses={400: {"model": ErrorResponse}},
)
async def verify_email(data: EmailVerificationRequest):
    """
    Verify email address.

    Uses verification token from email.
    """
    verification_service = VerificationService()

    success, error = verification_service.verify_email_with_token(data.token)

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return EmailVerificationResponse(message="Email verified successfully")

