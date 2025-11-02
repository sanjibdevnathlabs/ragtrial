"""
User repository with custom query methods.

Extends BaseRepository with user-specific operations.
"""

import trace.codes as codes
from typing import List, Optional

from sqlalchemy.orm import Session

import constants
from app.modules.user.entity import User
from database.base_repository import BaseRepository
from database.exceptions import DatabaseQueryError
from logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Repository for user operations.

    Extends BaseRepository with user-specific queries:
    - find_by_email()
    - find_active_users()
    - find_verified_users()
    - find_by_status()
    - mark_as_verified()
    - suspend_user()
    - activate_user()
    """

    def __init__(self):
        """Initialize user repository."""
        super().__init__(User)

    def find_by_email(
        self, session: Session, email: str, include_deleted: bool = False
    ) -> Optional[User]:
        """
        Find user by email address.

        Args:
            session: Database session
            email: Email address to search for
            include_deleted: Include soft-deleted users

        Returns:
            User if found, None otherwise
        """
        return self.find_by_field(session, "email", email, include_deleted)

    def find_active_users(self, session: Session) -> List[User]:
        """
        Find all active users (not deleted, status=active).

        Args:
            session: Database session

        Returns:
            List of active users
        """
        return self.find_by_fields(
            session,
            filters={"status": constants.USER_STATUS_ACTIVE},
            include_deleted=False,
        )

    def find_verified_users(
        self, session: Session, include_deleted: bool = False
    ) -> List[User]:
        """
        Find all verified users.

        Args:
            session: Database session
            include_deleted: Include soft-deleted users

        Returns:
            List of verified users
        """
        return self.find_by_fields(
            session, filters={"is_verified": True}, include_deleted=include_deleted
        )

    def find_unverified_users(
        self, session: Session, include_deleted: bool = False
    ) -> List[User]:
        """
        Find all unverified users.

        Args:
            session: Database session
            include_deleted: Include soft-deleted users

        Returns:
            List of unverified users
        """
        return self.find_by_fields(
            session, filters={"is_verified": False}, include_deleted=include_deleted
        )

    def find_by_status(
        self, session: Session, status: str, include_deleted: bool = False
    ) -> List[User]:
        """
        Find users by status.

        Args:
            session: Database session
            status: User status (active, inactive, suspended)
            include_deleted: Include soft-deleted users

        Returns:
            List of users with given status
        """
        return self.find_by_fields(
            session, filters={"status": status}, include_deleted=include_deleted
        )

    def mark_as_verified(self, session: Session, user_id: str) -> bool:
        """
        Mark user as verified.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            True if marked, False if not found

        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="mark_as_verified",
                user_id=user_id,
            )

            user = self.find_by_id(session, user_id)
            if user is None:
                logger.warning(codes.DB_ENTITY_NOT_FOUND, user_id=user_id)
                return False

            user.mark_as_verified()
            self.update(session, user)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="mark_as_verified",
                user_id=user_id,
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="mark_as_verified",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="mark_as_verified",
                details={"user_id": user_id},
                original_error=e,
            ) from e

    def suspend_user(self, session: Session, user_id: str) -> bool:
        """
        Suspend user account.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            True if suspended, False if not found

        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED, operation="suspend_user", user_id=user_id
            )

            user = self.find_by_id(session, user_id)
            if user is None:
                logger.warning(codes.DB_ENTITY_NOT_FOUND, user_id=user_id)
                return False

            user.suspend()
            self.update(session, user)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED, operation="suspend_user", user_id=user_id
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="suspend_user",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="suspend_user",
                details={"user_id": user_id},
                original_error=e,
            ) from e

    def activate_user(self, session: Session, user_id: str) -> bool:
        """
        Activate user account.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            True if activated, False if not found

        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED, operation="activate_user", user_id=user_id
            )

            user = self.find_by_id(session, user_id)
            if user is None:
                logger.warning(codes.DB_ENTITY_NOT_FOUND, user_id=user_id)
                return False

            user.activate()
            self.update(session, user)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="activate_user",
                user_id=user_id,
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="activate_user",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="activate_user",
                details={"user_id": user_id},
                original_error=e,
            ) from e

    def count_by_status(self, session: Session, status: str) -> int:
        """
        Count users by status.

        Args:
            session: Database session
            status: User status

        Returns:
            Count of users with given status
        """
        try:
            query = session.query(User).filter(
                User.status == status, User.deleted_at.is_(None)
            )
            return query.count()

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="count_by_status",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="count_by_status",
                details={"status": status},
                original_error=e,
            ) from e

