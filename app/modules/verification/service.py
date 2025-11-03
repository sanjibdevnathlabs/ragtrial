"""
Verification service for email verification.

Single responsibility: Email verification flow.
"""

import secrets
import trace.codes as codes
from typing import Optional, Tuple

from app.modules.user.service import UserService
from app.security.email_service import EmailService
from logger import get_logger

logger = get_logger(__name__)


class VerificationService:
    """
    Email verification service.

    Responsibilities:
    - Generate verification tokens
    - Send verification emails
    - Verify email with token
    - Resend verification emails
    """

    def __init__(self):
        """Initialize verification service."""
        self.user_service = UserService()
        self.email_service = EmailService()

    def send_verification_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Send verification email to user.

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

            if user.get("is_verified"):
                return False, "Email already verified"

            # Generate token
            token = secrets.token_urlsafe(32)

            # Send email
            self.email_service.send_verification_email(email, token)

            logger.info("verification_email_sent", email=email, user_id=user["id"])

            return True, None

        except Exception as e:
            logger.error(
                "verification_email_failed",
                email=email,
                error=str(e),
                exc_info=True,
            )
            return False, "Failed to send verification email"

    def verify_email_with_token(
        self, token: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify email using token.

        Args:
            token: Verification token

        Returns:
            Tuple of (success, error_message)

        Note: Token validation logic to be implemented
        """
        # TODO: Implement token storage and validation
        # For now, this is a placeholder
        return False, "Token validation not yet implemented"

    def resend_verification(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Resend verification email.

        Args:
            email: User email

        Returns:
            Tuple of (success, error_message)
        """
        return self.send_verification_email(email)

