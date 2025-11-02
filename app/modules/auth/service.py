"""
Authentication service.

Single responsibility: Login, logout, token operations.
"""

import trace.codes as codes
from typing import Dict, Optional, Tuple

from app.modules.token.service import TokenService
from app.modules.user.repository import UserRepository
from app.modules.user.service import UserService
from app.security.jwt_service import JWTService
from app.security.password import PasswordService
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service.

    Responsibilities:
    - User login
    - User logout (single and all sessions)
    - Token refresh
    - Token verification
    """

    def __init__(self):
        """Initialize auth service."""
        self.user_service = UserService()
        self.user_repository = UserRepository()
        self.token_service = TokenService()
        self.session_factory = SessionFactory()
        self.password_service = PasswordService()
        self.jwt_service = JWTService()

    def login(
        self, email: str, password: str, client_metadata: Optional[Dict] = None
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Authenticate user with credentials.

        Args:
            email: User email
            password: Plain text password
            client_metadata: Client info (user_agent, ip_address)

        Returns:
            Tuple of (tokens_dict, error_message)
        """
        try:
            logger.info(codes.DB_REPOSITORY_STARTED, operation="login", email=email)

            # Get user
            user = self.user_service.get_by_email(email)

            if not user:
                return None, "Invalid email or password"

            if not user.get("has_password"):
                return None, "Please use OAuth login"

            # Verify password
            with self.session_factory.get_read_session() as session:
                user_entity = self.user_repository.find_by_email(session, email)

                if not self.password_service.verify_password(
                    password, user_entity.password_hash
                ):
                    return None, "Invalid email or password"

            # Check active
            if not user.get("is_active"):
                return None, "Account is suspended"

            # Generate tokens
            tokens = self.jwt_service.generate_token_pair(user["id"], user["email"])

            # Store refresh token
            token_hash = JWTService.hash_token(tokens["refresh_token"])
            self.token_service.create_refresh_token(
                user["id"],
                token_hash,
                tokens["refresh_expires_at"],
                client_metadata,
            )

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="login",
                user_id=user["id"],
            )

            return tokens, None

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="login",
                error=str(e),
                exc_info=True,
            )
            return None, "Login failed"

    def refresh_token(
        self, refresh_token: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Refresh access token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            Tuple of (tokens_dict, error_message)
        """
        try:
            # Validate JWT
            payload = self.jwt_service.validate_refresh_token(refresh_token)

            if not payload:
                return None, "Invalid or expired refresh token"

            user_id = payload.get("user_id")

            # Check database
            token_hash = JWTService.hash_token(refresh_token)
            token_entity = self.token_service.find_by_hash(token_hash)

            if not token_entity or not token_entity.is_valid():
                return None, "Token has been revoked"

            # Check user active
            with self.session_factory.get_read_session() as session:
                user = self.user_repository.find_by_id(session, user_id)

                if not user or not user.is_active():
                    return None, "User account not active"

            # Generate new access token
            access_token = self.jwt_service.generate_access_token(user.id, user.email)

            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": self.jwt_service.access_token_expire_minutes * 60,
            }, None

        except Exception as e:
            logger.error("token_refresh_failed", error=str(e), exc_info=True)
            return None, "Token refresh failed"

    def logout(self, refresh_token: str) -> Tuple[bool, Optional[str]]:
        """
        Logout single session.

        Args:
            refresh_token: JWT refresh token

        Returns:
            Tuple of (success, error_message)
        """
        try:
            token_hash = JWTService.hash_token(refresh_token)
            success = self.token_service.revoke_token(token_hash)

            if success:
                return True, None

            return False, "Token not found"

        except Exception as e:
            logger.error("logout_failed", error=str(e), exc_info=True)
            return False, "Logout failed"

    def logout_all(self, user_id: str) -> Tuple[int, Optional[str]]:
        """
        Logout all sessions.

        Args:
            user_id: User ID

        Returns:
            Tuple of (count_revoked, error_message)
        """
        try:
            count = self.token_service.revoke_all_user_tokens(user_id)
            return count, None

        except Exception as e:
            logger.error("logout_all_failed", error=str(e), exc_info=True)
            return 0, "Logout all failed"

    def verify_token(self, access_token: str) -> Optional[Dict]:
        """
        Verify access token.

        Args:
            access_token: JWT access token

        Returns:
            User dict if valid, None otherwise
        """
        payload = self.jwt_service.validate_access_token(access_token)

        if not payload:
            return None

        user_id = payload.get("user_id")
        return self.user_service.get_by_id(user_id)

