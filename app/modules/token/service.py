"""
Token service for refresh token management.

Single responsibility: Token CRUD operations.
"""

import trace.codes as codes
from typing import Optional

from app.modules.token.entity import RefreshToken
from app.modules.token.repository import RefreshTokenRepository
from app.security.jwt_service import JWTService
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class TokenService:
    """
    Token CRUD service.

    Responsibilities:
    - Create refresh tokens
    - Find tokens
    - Revoke tokens
    - Clean up expired tokens
    """

    def __init__(self):
        """Initialize token service."""
        self.repository = RefreshTokenRepository()
        self.session_factory = SessionFactory()

    def create_refresh_token(
        self,
        user_id: str,
        token_hash: str,
        expires_at: int,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Create and store refresh token.

        Args:
            user_id: User ID
            token_hash: Hashed token
            expires_at: Expiration timestamp (ms)
            metadata: Client metadata

        Returns:
            Token ID
        """
        token = RefreshToken(
            id=RefreshToken.generate_id(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        if metadata:
            token.set_metadata(metadata)

        with self.session_factory.get_write_session() as session:
            created = self.repository.create(session, token)
            # Extract ID while session is still open
            token_id = created.id

        return token_id

    def find_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Find token by hash."""
        with self.session_factory.get_read_session() as session:
            return self.repository.find_by_token_hash(session, token_hash)

    def revoke_token(self, token_hash: str) -> bool:
        """Revoke single token."""
        with self.session_factory.get_write_session() as session:
            return self.repository.revoke_token(session, token_hash)

    def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for user."""
        logger.info(codes.DB_REPOSITORY_STARTED, operation="revoke_all", user_id=user_id)

        with self.session_factory.get_write_session() as session:
            count = self.repository.revoke_all_user_tokens(session, user_id)

        logger.info(
            codes.DB_REPOSITORY_COMPLETED,
            operation="revoke_all",
            user_id=user_id,
            count=count,
        )

        return count

    def cleanup_expired(self) -> int:
        """Remove expired tokens."""
        with self.session_factory.get_write_session() as session:
            return self.repository.cleanup_expired(session)

