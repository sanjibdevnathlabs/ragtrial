"""
Token repository with custom query methods.

Handles both RefreshToken and PasswordResetToken entities.
"""

import trace.codes as codes
from typing import List, Optional

from sqlalchemy.orm import Session

import constants
from app.modules.token.entity import PasswordResetToken, RefreshToken
from database.base_repository import BaseRepository
from database.exceptions import DatabaseQueryError
from logger import get_logger

logger = get_logger(__name__)


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Repository for refresh token operations.

    Extends BaseRepository with token-specific queries:
    - find_by_token_hash()
    - find_by_user_id()
    - find_active_tokens()
    - find_expired_tokens()
    - revoke_token()
    - revoke_all_user_tokens()
    - cleanup_expired_tokens()
    """

    def __init__(self):
        """Initialize refresh token repository."""
        super().__init__(RefreshToken)

    def find_by_token_hash(
        self, session: Session, token_hash: str, include_deleted: bool = False
    ) -> Optional[RefreshToken]:
        """
        Find refresh token by token hash.

        Args:
            session: Database session
            token_hash: SHA-256 hash of token
            include_deleted: Include soft-deleted tokens

        Returns:
            RefreshToken if found, None otherwise
        """
        return self.find_by_field(session, "token_hash", token_hash, include_deleted)

    def find_by_user_id(
        self, session: Session, user_id: str, include_deleted: bool = False
    ) -> List[RefreshToken]:
        """
        Find all refresh tokens for a user.

        Args:
            session: Database session
            user_id: User ID
            include_deleted: Include soft-deleted tokens

        Returns:
            List of refresh tokens
        """
        return self.find_by_fields(
            session, filters={"user_id": user_id}, include_deleted=include_deleted
        )

    def find_active_tokens(
        self, session: Session, user_id: str
    ) -> List[RefreshToken]:
        """
        Find all active (valid) refresh tokens for a user.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            List of active refresh tokens
        """
        try:
            current_time = RefreshToken._get_current_timestamp()
            
            query = session.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.expires_at > current_time,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.deleted_at.is_(None),
            )
            
            return query.all()

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="find_active_tokens",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="find_active_tokens",
                details={"user_id": user_id},
                original_error=e,
            ) from e

    def find_expired_tokens(self, session: Session) -> List[RefreshToken]:
        """
        Find all expired refresh tokens.

        Args:
            session: Database session

        Returns:
            List of expired tokens
        """
        try:
            current_time = RefreshToken._get_current_timestamp()
            
            query = session.query(RefreshToken).filter(
                RefreshToken.expires_at <= current_time,
                RefreshToken.deleted_at.is_(None),
            )
            
            return query.all()

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="find_expired_tokens",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="find_expired_tokens",
                original_error=e,
            ) from e

    def revoke_token(self, session: Session, token_hash: str) -> bool:
        """
        Revoke a refresh token.

        Args:
            session: Database session
            token_hash: Token hash to revoke

        Returns:
            True if revoked, False if not found

        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="revoke_token",
                token_hash=token_hash[:10] + "...",
            )

            token = self.find_by_token_hash(session, token_hash)
            if token is None:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND, token_hash=token_hash[:10] + "..."
                )
                return False

            token.revoke()
            self.update(session, token)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="revoke_token",
                token_hash=token_hash[:10] + "...",
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="revoke_token",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="revoke_token",
                details={"token_hash": token_hash[:10] + "..."},
                original_error=e,
            ) from e

    def revoke_all_user_tokens(self, session: Session, user_id: str) -> int:
        """
        Revoke all active refresh tokens for a user.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Number of tokens revoked

        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="revoke_all_user_tokens",
                user_id=user_id,
            )

            tokens = self.find_active_tokens(session, user_id)
            count = 0

            for token in tokens:
                token.revoke()
                self.update(session, token)
                count += 1

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="revoke_all_user_tokens",
                user_id=user_id,
                count=count,
            )

            return count

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="revoke_all_user_tokens",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="revoke_all_user_tokens",
                details={"user_id": user_id},
                original_error=e,
            ) from e

    def cleanup_expired_tokens(self, session: Session) -> int:
        """
        Soft delete all expired refresh tokens.

        Args:
            session: Database session

        Returns:
            Number of tokens cleaned up

        Raises:
            DatabaseQueryError: If delete fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED, operation="cleanup_expired_tokens"
            )

            tokens = self.find_expired_tokens(session)
            count = 0

            for token in tokens:
                self.soft_delete(session, token.id)
                count += 1

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="cleanup_expired_tokens",
                count=count,
            )

            return count

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="cleanup_expired_tokens",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_DELETE_FAILED,
                query="cleanup_expired_tokens",
                original_error=e,
            ) from e


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    """
    Repository for password reset token operations.

    Extends BaseRepository with token-specific queries:
    - find_by_token_hash()
    - find_by_user_id()
    - find_active_token()
    - mark_as_used()
    - cleanup_expired_tokens()
    - invalidate_user_tokens()
    """

    def __init__(self):
        """Initialize password reset token repository."""
        super().__init__(PasswordResetToken)

    def find_by_token_hash(
        self, session: Session, token_hash: str, include_deleted: bool = False
    ) -> Optional[PasswordResetToken]:
        """
        Find password reset token by token hash.

        Args:
            session: Database session
            token_hash: SHA-256 hash of token
            include_deleted: Include soft-deleted tokens

        Returns:
            PasswordResetToken if found, None otherwise
        """
        return self.find_by_field(session, "token_hash", token_hash, include_deleted)

    def find_by_user_id(
        self, session: Session, user_id: str, include_deleted: bool = False
    ) -> List[PasswordResetToken]:
        """
        Find all password reset tokens for a user.

        Args:
            session: Database session
            user_id: User ID
            include_deleted: Include soft-deleted tokens

        Returns:
            List of password reset tokens
        """
        return self.find_by_fields(
            session, filters={"user_id": user_id}, include_deleted=include_deleted
        )

    def find_active_token(
        self, session: Session, user_id: str
    ) -> Optional[PasswordResetToken]:
        """
        Find the active (valid) password reset token for a user.

        Only one active token should exist per user.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Active PasswordResetToken if found, None otherwise
        """
        try:
            current_time = PasswordResetToken._get_current_timestamp()
            
            query = session.query(PasswordResetToken).filter(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.expires_at > current_time,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.deleted_at.is_(None),
            )
            
            return query.first()

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="find_active_token",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="find_active_token",
                details={"user_id": user_id},
                original_error=e,
            ) from e

    def mark_as_used(self, session: Session, token_hash: str) -> bool:
        """
        Mark password reset token as used.

        Args:
            session: Database session
            token_hash: Token hash to mark as used

        Returns:
            True if marked, False if not found

        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="mark_as_used",
                token_hash=token_hash[:10] + "...",
            )

            token = self.find_by_token_hash(session, token_hash)
            if token is None:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND, token_hash=token_hash[:10] + "..."
                )
                return False

            token.mark_as_used()
            self.update(session, token)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="mark_as_used",
                token_hash=token_hash[:10] + "...",
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="mark_as_used",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="mark_as_used",
                details={"token_hash": token_hash[:10] + "..."},
                original_error=e,
            ) from e

    def cleanup_expired_tokens(self, session: Session) -> int:
        """
        Soft delete all expired password reset tokens.

        Args:
            session: Database session

        Returns:
            Number of tokens cleaned up

        Raises:
            DatabaseQueryError: If delete fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED, operation="cleanup_expired_tokens"
            )

            current_time = PasswordResetToken._get_current_timestamp()
            
            query = session.query(PasswordResetToken).filter(
                PasswordResetToken.expires_at <= current_time,
                PasswordResetToken.deleted_at.is_(None),
            )
            
            tokens = query.all()
            count = 0

            for token in tokens:
                self.soft_delete(session, token.id)
                count += 1

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="cleanup_expired_tokens",
                count=count,
            )

            return count

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="cleanup_expired_tokens",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_DELETE_FAILED,
                query="cleanup_expired_tokens",
                original_error=e,
            ) from e

    def invalidate_user_tokens(self, session: Session, user_id: str) -> int:
        """
        Soft delete all password reset tokens for a user.

        Used when user successfully resets password or when new token is issued.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Number of tokens invalidated

        Raises:
            DatabaseQueryError: If delete fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="invalidate_user_tokens",
                user_id=user_id,
            )

            tokens = self.find_by_user_id(session, user_id, include_deleted=False)
            count = 0

            for token in tokens:
                if not token.is_deleted():
                    self.soft_delete(session, token.id)
                    count += 1

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="invalidate_user_tokens",
                user_id=user_id,
                count=count,
            )

            return count

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="invalidate_user_tokens",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_DELETE_FAILED,
                query="invalidate_user_tokens",
                details={"user_id": user_id},
                original_error=e,
            ) from e

