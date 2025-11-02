"""
UserRole repository with custom query methods.

Extends BaseRepository with user-role mapping operations.
"""

import time
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.user_role.entity import UserRole
from database.base_repository import BaseRepository
from logger import get_logger

logger = get_logger(__name__)


class UserRoleRepository(BaseRepository[UserRole]):
    """
    Repository for user role mapping operations.

    Extends BaseRepository with user-role-specific queries:
    - find_by_user_id()
    - find_by_role_id()
    - find_by_user_and_role()
    - find_active_by_user_id()
    """

    def __init__(self):
        """Initialize user role repository."""
        super().__init__(UserRole)

    def find_by_user_id(
        self, session: Session, user_id: str, include_deleted: bool = False
    ) -> List[UserRole]:
        """
        Find all role assignments for a user.

        Args:
            session: Database session
            user_id: User UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            List of user role assignments
        """
        query = session.query(UserRole).filter(UserRole.user_id == user_id)

        if not include_deleted:
            query = query.filter(UserRole.deleted_at.is_(None))

        return query.all()

    def find_by_role_id(
        self, session: Session, role_id: str, include_deleted: bool = False
    ) -> List[UserRole]:
        """
        Find all users assigned to a role.

        Args:
            session: Database session
            role_id: Role UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            List of user role assignments
        """
        query = session.query(UserRole).filter(UserRole.role_id == role_id)

        if not include_deleted:
            query = query.filter(UserRole.deleted_at.is_(None))

        return query.all()

    def find_by_user_and_role(
        self,
        session: Session,
        user_id: str,
        role_id: str,
        include_deleted: bool = False,
    ) -> Optional[UserRole]:
        """
        Find specific user-role assignment.

        Args:
            session: Database session
            user_id: User UUID
            role_id: Role UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            UserRole if found, None otherwise
        """
        query = session.query(UserRole).filter(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )

        if not include_deleted:
            query = query.filter(UserRole.deleted_at.is_(None))

        return query.first()

    def find_active_by_user_id(self, session: Session, user_id: str) -> List[UserRole]:
        """
        Find all active (non-expired, non-deleted) role assignments for a user.

        Args:
            session: Database session
            user_id: User UUID

        Returns:
            List of active user role assignments
        """
        current_time_ms = int(time.time() * 1000)

        query = session.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.deleted_at.is_(None),
        )

        # Filter out expired roles
        # Either expires_at is NULL (never expires) OR expires_at > current_time
        query = query.filter(
            (UserRole.expires_at.is_(None)) | (UserRole.expires_at > current_time_ms)
        )

        return query.all()

