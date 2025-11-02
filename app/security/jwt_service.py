"""
JWT token generation and validation service.

Handles access and refresh tokens for authentication.
"""

import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

import jwt

import constants
from config import Config
from logger import get_logger

logger = get_logger(__name__)


class JWTService:
    """
    Service for JWT token generation and validation.

    Handles:
    - Access token generation (short-lived)
    - Refresh token generation (long-lived)
    - Token validation and parsing
    - Token hashing for storage
    """

    def __init__(self):
        """Initialize JWT service with config."""
        self.config = Config()
        self.secret = self.config.auth.jwt_secret
        self.algorithm = self.config.auth.jwt_algorithm
        self.access_token_expire_minutes = self.config.auth.access_token_expire_minutes
        self.refresh_token_expire_days = self.config.auth.refresh_token_expire_days

        if not self.secret:
            raise ValueError("JWT_SECRET not configured")

    def generate_access_token(self, user_id: str, email: str) -> str:
        """
        Generate access token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            JWT access token string
        """
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )

        payload = {
            "user_id": user_id,
            "email": email,
            "type": "access",
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }

        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token

    def generate_refresh_token(self, user_id: str) -> Tuple[str, int]:
        """
        Generate refresh token.

        Args:
            user_id: User ID

        Returns:
            Tuple of (token_string, expires_at_milliseconds)
        """
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expire_days
        )

        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }

        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        
        # Return token and expires_at in milliseconds
        expires_at_ms = int(expires_at.timestamp() * 1000)
        
        return token, expires_at_ms

    def validate_token(self, token: str, token_type: str = "access") -> Optional[Dict]:
        """
        Validate and decode JWT token.

        Args:
            token: JWT token string
            token_type: Expected token type (access/refresh)

        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=[self.algorithm]
            )

            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(
                    "token_type_mismatch",
                    expected=token_type,
                    actual=payload.get("type"),
                )
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.info("token_expired", token_type=token_type)
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("token_invalid", error=str(e))
            return None
        except Exception as e:
            logger.error("token_validation_error", error=str(e), exc_info=True)
            return None

    def validate_access_token(self, token: str) -> Optional[Dict]:
        """
        Validate access token.

        Args:
            token: JWT access token

        Returns:
            Decoded payload if valid, None otherwise
        """
        return self.validate_token(token, token_type="access")

    def validate_refresh_token(self, token: str) -> Optional[Dict]:
        """
        Validate refresh token.

        Args:
            token: JWT refresh token

        Returns:
            Decoded payload if valid, None otherwise
        """
        return self.validate_token(token, token_type="refresh")

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from token (without full validation).

        Args:
            token: JWT token

        Returns:
            User ID if present, None otherwise
        """
        try:
            # Decode without verification (for revoked token check)
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            return payload.get("user_id")
        except Exception:
            return None

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash token for secure storage.

        Uses SHA-256 for fast, deterministic hashing.

        Args:
            token: JWT token string

        Returns:
            SHA-256 hex digest
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def generate_token_pair(self, user_id: str, email: str) -> Dict[str, any]:
        """
        Generate access and refresh token pair.

        Args:
            user_id: User ID
            email: User email

        Returns:
            Dictionary with access_token, refresh_token, expires_in
        """
        access_token = self.generate_access_token(user_id, email)
        refresh_token, refresh_expires_at_ms = self.generate_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_expire_minutes * 60,  # seconds
            "refresh_expires_at": refresh_expires_at_ms,
        }

    def decode_token_unsafe(self, token: str) -> Optional[Dict]:
        """
        Decode token without validation (for debugging/logging).

        WARNING: Do not use for authentication!

        Args:
            token: JWT token

        Returns:
            Decoded payload or None
        """
        try:
            return jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_signature": False, "verify_exp": False}
            )
        except Exception:
            return None

