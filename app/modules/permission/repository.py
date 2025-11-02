"""
Permission repository with custom query methods.

Extends BaseRepository with permission-specific operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.permission.entity import Permission
from database.base_repository import BaseRepository
from logger import get_logger

logger = get_logger(__name__)


class PermissionRepository(BaseRepository[Permission]):
    """
    Repository for permission operations.

    Extends BaseRepository with permission-specific queries:
    - find_by_name()
    - find_by_resource()
    - find_by_action()
    - find_by_resource_and_action()
    - find_all_active()
    """

    def __init__(self):
        """Initialize permission repository."""
        super().__init__(Permission)

    def find_by_name(
        self, session: Session, name: str, include_deleted: bool = False
    ) -> Optional[Permission]:
        """
        Find permission by name.

        Args:
            session: Database session
            name: Permission name (case-sensitive, format: 'resource:action')
            include_deleted: Include soft-deleted permissions

        Returns:
            Permission if found, None otherwise
        """
        return self.find_by_field(session, "name", name, include_deleted)

    def find_by_resource(
        self, session: Session, resource: str, include_deleted: bool = False
    ) -> List[Permission]:
        """
        Find all permissions for a resource.

        Args:
            session: Database session
            resource: Resource type (e.g., 'user', 'file')
            include_deleted: Include soft-deleted permissions

        Returns:
            List of permissions for the resource
        """
        query = session.query(Permission).filter(Permission.resource == resource)

        if not include_deleted:
            query = query.filter(Permission.deleted_at.is_(None))

        return query.all()

    def find_by_action(
        self, session: Session, action: str, include_deleted: bool = False
    ) -> List[Permission]:
        """
        Find all permissions for an action.

        Args:
            session: Database session
            action: Action type (e.g., 'read', 'write')
            include_deleted: Include soft-deleted permissions

        Returns:
            List of permissions for the action
        """
        query = session.query(Permission).filter(Permission.action == action)

        if not include_deleted:
            query = query.filter(Permission.deleted_at.is_(None))

        return query.all()

    def find_by_resource_and_action(
        self,
        session: Session,
        resource: str,
        action: str,
        include_deleted: bool = False,
    ) -> Optional[Permission]:
        """
        Find permission by resource and action.

        Args:
            session: Database session
            resource: Resource type
            action: Action type
            include_deleted: Include soft-deleted permissions

        Returns:
            Permission if found, None otherwise
        """
        query = session.query(Permission).filter(
            Permission.resource == resource, Permission.action == action
        )

        if not include_deleted:
            query = query.filter(Permission.deleted_at.is_(None))

        return query.first()

    def find_all_active(self, session: Session) -> List[Permission]:
        """
        Find all active (non-deleted) permissions.

        Args:
            session: Database session

        Returns:
            List of active permissions
        """
        return self.find_all(session, include_deleted=False)

