"""
UserPermission repository with custom query methods.

Extends BaseRepository with user-permission mapping operations.
"""

import time
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.user_permission.entity import UserPermission
from database.base_repository import BaseRepository
from logger import get_logger

logger = get_logger(__name__)


class UserPermissionRepository(BaseRepository[UserPermission]):
    """
    Repository for user permission mapping operations.

    Extends BaseRepository with user-permission-specific queries:
    - find_by_user_id()
    - find_by_permission_id()
    - find_by_user_and_permission()
    - find_active_by_user_id()
    """

    def __init__(self):
        """Initialize user permission repository."""
        super().__init__(UserPermission)

    def find_by_user_id(
        self, session: Session, user_id: str, include_deleted: bool = False
    ) -> List[UserPermission]:
        """
        Find all direct permission assignments for a user.

        Args:
            session: Database session
            user_id: User UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            List of user permission assignments
        """
        query = session.query(UserPermission).filter(
            UserPermission.user_id == user_id
        )

        if not include_deleted:
            query = query.filter(UserPermission.deleted_at.is_(None))

        return query.all()

    def find_by_permission_id(
        self, session: Session, permission_id: str, include_deleted: bool = False
    ) -> List[UserPermission]:
        """
        Find all users with direct assignment of a permission.

        Args:
            session: Database session
            permission_id: Permission UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            List of user permission assignments
        """
        query = session.query(UserPermission).filter(
            UserPermission.permission_id == permission_id
        )

        if not include_deleted:
            query = query.filter(UserPermission.deleted_at.is_(None))

        return query.all()

    def find_by_user_and_permission(
        self,
        session: Session,
        user_id: str,
        permission_id: str,
        include_deleted: bool = False,
    ) -> Optional[UserPermission]:
        """
        Find specific user-permission assignment.

        Args:
            session: Database session
            user_id: User UUID
            permission_id: Permission UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            UserPermission if found, None otherwise
        """
        query = session.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id,
        )

        if not include_deleted:
            query = query.filter(UserPermission.deleted_at.is_(None))

        return query.first()

    def find_active_by_user_id(
        self, session: Session, user_id: str
    ) -> List[UserPermission]:
        """
        Find all active (non-expired, non-deleted) direct permission assignments for a user.

        Args:
            session: Database session
            user_id: User UUID

        Returns:
            List of active user permission assignments
        """
        current_time_ms = int(time.time() * 1000)

        query = session.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.deleted_at.is_(None),
        )

        # Filter out expired permissions
        # Either expires_at is NULL (never expires) OR expires_at > current_time
        query = query.filter(
            (UserPermission.expires_at.is_(None))
            | (UserPermission.expires_at > current_time_ms)
        )

        return query.all()

