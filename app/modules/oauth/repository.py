"""
OAuth Provider repository with custom query methods.

Extends BaseRepository with OAuth provider-specific operations.
"""

import trace.codes as codes
from typing import List, Optional

from sqlalchemy.orm import Session

import constants
from app.modules.oauth.entity import OAuthProvider
from database.base_repository import BaseRepository
from database.exceptions import DatabaseQueryError
from logger import get_logger

logger = get_logger(__name__)


class OAuthProviderRepository(BaseRepository[OAuthProvider]):
    """
    Repository for OAuth provider operations.

    Extends BaseRepository with OAuth-specific queries:
    - find_by_user_id()
    - find_by_provider()
    - find_by_provider_user_id()
    - find_user_provider()
    """

    def __init__(self):
        """Initialize OAuth provider repository."""
        super().__init__(OAuthProvider)

    def find_by_user_id(
        self, session: Session, user_id: str, include_deleted: bool = False
    ) -> List[OAuthProvider]:
        """
        Find all OAuth providers for a user.

        Args:
            session: Database session
            user_id: User ID
            include_deleted: Include soft-deleted providers

        Returns:
            List of OAuth providers for the user
        """
        return self.find_by_fields(
            session, filters={"user_id": user_id}, include_deleted=include_deleted
        )

    def find_by_provider(
        self, session: Session, provider: str, include_deleted: bool = False
    ) -> List[OAuthProvider]:
        """
        Find all OAuth providers of a specific type.

        Args:
            session: Database session
            provider: Provider name (google, github)
            include_deleted: Include soft-deleted providers

        Returns:
            List of OAuth providers
        """
        return self.find_by_fields(
            session, filters={"provider": provider}, include_deleted=include_deleted
        )

    def find_by_provider_user_id(
        self,
        session: Session,
        provider: str,
        provider_user_id: str,
        include_deleted: bool = False,
    ) -> Optional[OAuthProvider]:
        """
        Find OAuth provider by provider and provider_user_id.

        Args:
            session: Database session
            provider: Provider name (google, github)
            provider_user_id: User ID from the OAuth provider
            include_deleted: Include soft-deleted providers

        Returns:
            OAuthProvider if found, None otherwise
        """
        return self.find_by_fields(
            session,
            filters={"provider": provider, "provider_user_id": provider_user_id},
            include_deleted=include_deleted,
        ).first() if self.find_by_fields(
            session,
            filters={"provider": provider, "provider_user_id": provider_user_id},
            include_deleted=include_deleted,
        ) else None

    def find_user_provider(
        self, session: Session, user_id: str, provider: str, include_deleted: bool = False
    ) -> Optional[OAuthProvider]:
        """
        Find specific OAuth provider for a user.

        Args:
            session: Database session
            user_id: User ID
            provider: Provider name (google, github)
            include_deleted: Include soft-deleted providers

        Returns:
            OAuthProvider if found, None otherwise
        """
        results = self.find_by_fields(
            session,
            filters={"user_id": user_id, "provider": provider},
            include_deleted=include_deleted,
        )
        return results[0] if results else None

    def user_has_provider(
        self, session: Session, user_id: str, provider: str
    ) -> bool:
        """
        Check if user has a specific OAuth provider linked.

        Args:
            session: Database session
            user_id: User ID
            provider: Provider name (google, github)

        Returns:
            True if provider is linked, False otherwise
        """
        return self.find_user_provider(session, user_id, provider) is not None

    def count_by_provider(self, session: Session, provider: str) -> int:
        """
        Count OAuth providers by type.

        Args:
            session: Database session
            provider: Provider name (google, github)

        Returns:
            Count of providers
        """
        try:
            query = session.query(OAuthProvider).filter(
                OAuthProvider.provider == provider, OAuthProvider.deleted_at.is_(None)
            )
            return query.count()

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="count_by_provider",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="count_by_provider",
                details={"provider": provider},
                original_error=e,
            ) from e

