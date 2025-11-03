"""
Password hashing and verification utilities.

Uses bcrypt for secure password hashing.
"""

import bcrypt
from typing import Optional

import constants
from logger import get_logger

logger = get_logger(__name__)


class PasswordService:
    """
    Service for password hashing and verification.

    Uses bcrypt with cost factor 12 for good security/performance balance.
    """

    # Bcrypt cost factor (number of rounds = 2^cost)
    # Cost 12 = ~250ms on modern hardware
    BCRYPT_COST = 12

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Bcrypt hash string

        Raises:
            ValueError: If password is empty or too long
        """
        if not password:
            raise ValueError(constants.ERROR_INVALID_INPUT)

        if len(password) > 72:  # Bcrypt limitation
            raise ValueError("Password too long (max 72 characters)")

        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=PasswordService.BCRYPT_COST)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password to verify
            password_hash: Bcrypt hash to verify against

        Returns:
            True if password matches, False otherwise
        """
        if not password or not password_hash:
            return False

        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except Exception as e:
            logger.error(
                "password_verification_failed",
                error=str(e),
                exc_info=True,
            )
            return False

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if len(password) > 72:
            return False, "Password too long (max 72 characters)"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        return True, None

