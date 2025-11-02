"""
Password service for password operations.

Single responsibility: Password change and reset flows.
"""

import secrets
import trace.codes as codes
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from app.modules.token.entity import PasswordResetToken
from app.modules.token.repository import PasswordResetTokenRepository
from app.modules.token.service import TokenService
from app.modules.user.repository import UserRepository
from app.modules.user.service import UserService
from app.security.email_service import EmailService
from app.security.jwt_service import JWTService
from app.security.password import PasswordService as PasswordHashService
from config import Config
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class PasswordService:
    """
    Password management service.

    Responsibilities:
    - Change password (with old password verification)
    - Request password reset
    - Reset password with token
    - Send notification emails
    """

    def __init__(self):
        """Initialize password service."""
        self.user_service = UserService()
        self.user_repository = UserRepository()
        self.token_service = TokenService()
        self.reset_repository = PasswordResetTokenRepository()
        self.session_factory = SessionFactory()
        self.password_hash_service = PasswordHashService()
        self.email_service = EmailService()
        self.config = Config()

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password with verification.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate new password
            is_valid, error_msg = self.password_hash_service.validate_password_strength(
                new_password
            )
            if not is_valid:
                return False, error_msg

            # Get user
            with self.session_factory.get_read_session() as session:
                user = self.user_repository.find_by_id(session, user_id)

                if not user:
                    return False, "User not found"

                if not user.password_hash:
                    return False, "OAuth user cannot change password this way"

                # Verify old password
                if not self.password_hash_service.verify_password(
                    old_password, user.password_hash
                ):
                    return False, "Current password is incorrect"

            # Update password
            password_hash = self.password_hash_service.hash_password(new_password)

            with self.session_factory.get_write_session() as session:
                user = self.user_repository.find_by_id(session, user_id)
                user.password_hash = password_hash
                self.user_repository.update(session, user)

            # Send notification
            user_data = self.user_service.get_by_id(user_id)
            if user_data:
                self.email_service.send_password_changed_notification(
                    user_data["email"]
                )

            return True, None

        except Exception as e:
            logger.error("password_change_failed", error=str(e), exc_info=True)
            return False, "Password change failed"

    def request_reset(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Request password reset.

        Args:
            email: User email

        Returns:
            Tuple of (success, error_message)
        """
        try:
            user = self.user_service.get_by_email(email)

            if not user:
                # Don't reveal if user exists
                return True, None

            user_id = user["id"]

            # Invalidate existing tokens
            with self.session_factory.get_write_session() as session:
                self.reset_repository.invalidate_user_tokens(session, user_id)

            # Generate token
            token = secrets.token_urlsafe(32)
            token_hash = JWTService.hash_token(token)

            # Calculate expiration
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.auth.password_reset_expire_minutes
            )
            expires_at_ms = int(expires_at.timestamp() * 1000)

            # Store token
            reset_token = PasswordResetToken(
                id=PasswordResetToken.generate_id(),
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at_ms,
            )

            with self.session_factory.get_write_session() as session:
                self.reset_repository.create(session, reset_token)

            # Send email
            self.email_service.send_password_reset_email(email, token)

            logger.info("password_reset_requested", user_id=user_id)

            return True, None

        except Exception as e:
            logger.error("password_reset_request_failed", error=str(e), exc_info=True)
            return False, "Password reset request failed"

    def reset_with_token(
        self, token: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Reset password using token.

        Args:
            token: Reset token
            new_password: New password

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate password
            is_valid, error_msg = self.password_hash_service.validate_password_strength(
                new_password
            )
            if not is_valid:
                return False, error_msg

            # Find token
            token_hash = JWTService.hash_token(token)

            with self.session_factory.get_read_session() as session:
                token_entity = self.reset_repository.find_by_token_hash(
                    session, token_hash
                )

                if not token_entity or not token_entity.is_valid():
                    return False, "Invalid or expired reset token"

                user_id = token_entity.user_id

            # Update password
            password_hash = self.password_hash_service.hash_password(new_password)

            with self.session_factory.get_write_session() as session:
                user = self.user_repository.find_by_id(session, user_id)
                user.password_hash = password_hash
                self.user_repository.update(session, user)

                # Mark token as used
                self.reset_repository.mark_as_used(session, token_hash)

            # Revoke all sessions
            self.token_service.revoke_all_user_tokens(user_id)

            # Send notification
            user_data = self.user_service.get_by_id(user_id)
            if user_data:
                self.email_service.send_password_changed_notification(
                    user_data["email"]
                )

            return True, None

        except Exception as e:
            logger.error("password_reset_failed", error=str(e), exc_info=True)
            return False, "Password reset failed"

