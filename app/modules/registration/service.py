"""
Registration service for user signup.

Single responsibility: User registration flow.
"""

import secrets
import trace.codes as codes
from typing import Dict, Optional, Tuple

from app.modules.user.service import UserService
from app.security.email_service import EmailService
from app.security.password import PasswordService
from logger import get_logger

logger = get_logger(__name__)


class RegistrationService:
    """
    User registration service.

    Responsibilities:
    - Validate registration data
    - Create new user accounts
    - Generate verification tokens
    - Send verification emails
    """

    def __init__(self):
        """Initialize registration service."""
        self.user_service = UserService()
        self.password_service = PasswordService()
        self.email_service = EmailService()

    def register_user(
        self, email: str, full_name: str, password: str
    ) -> Tuple[Dict, Optional[str]]:
        """
        Register new user with password.

        Args:
            email: User email
            full_name: User full name
            password: Plain text password

        Returns:
            Tuple of (user_dict, error_message)
        """
        try:
            logger.info(codes.DB_REPOSITORY_STARTED, operation="register", email=email)

            # Validate password strength
            is_valid, error_msg = self.password_service.validate_password_strength(
                password
            )
            if not is_valid:
                return None, error_msg

            # Hash password
            password_hash = self.password_service.hash_password(password)

            # Create user
            user = self.user_service.create_user(email, full_name, password_hash)

            # Generate verification token
            verification_token = secrets.token_urlsafe(32)

            # Send verification email
            self.email_service.send_verification_email(email, verification_token)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="register",
                user_id=user["id"],
            )

            return user, None

        except ValueError as e:
            logger.warning("registration_failed", email=email, error=str(e))
            return None, str(e)
        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="register",
                error=str(e),
                exc_info=True,
            )
            return None, "Registration failed"

    def register_oauth_user(
        self, email: str, full_name: str, avatar_url: Optional[str] = None
    ) -> Dict:
        """
        Register new user from OAuth (no password).

        Args:
            email: User email
            full_name: User full name
            avatar_url: Avatar URL from OAuth

        Returns:
            Created user dictionary

        Raises:
            ValueError: If user creation fails
        """
        user = self.user_service.create_user(email, full_name, password_hash=None)

        # Update avatar if provided
        if avatar_url:
            self.user_service.update_profile(user["id"], avatar_url=avatar_url)

        # Auto-verify OAuth users
        self.user_service.mark_verified(user["id"])

        return user

