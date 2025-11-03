"""
RolePermission repository with custom query methods.

Extends BaseRepository with role-permission mapping operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.role_permission.entity import RolePermission
from database.base_repository import BaseRepository
from logger import get_logger

logger = get_logger(__name__)


class RolePermissionRepository(BaseRepository[RolePermission]):
    """
    Repository for role permission mapping operations.

    Extends BaseRepository with role-permission-specific queries:
    - find_by_role_id()
    - find_by_permission_id()
    - find_by_role_and_permission()
    """

    def __init__(self):
        """Initialize role permission repository."""
        super().__init__(RolePermission)

    def find_by_role_id(
        self, session: Session, role_id: str, include_deleted: bool = False
    ) -> List[RolePermission]:
        """
        Find all permissions assigned to a role.

        Args:
            session: Database session
            role_id: Role UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            List of role permission assignments
        """
        query = session.query(RolePermission).filter(
            RolePermission.role_id == role_id
        )

        if not include_deleted:
            query = query.filter(RolePermission.deleted_at.is_(None))

        return query.all()

    def find_by_permission_id(
        self, session: Session, permission_id: str, include_deleted: bool = False
    ) -> List[RolePermission]:
        """
        Find all roles that have a permission.

        Args:
            session: Database session
            permission_id: Permission UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            List of role permission assignments
        """
        query = session.query(RolePermission).filter(
            RolePermission.permission_id == permission_id
        )

        if not include_deleted:
            query = query.filter(RolePermission.deleted_at.is_(None))

        return query.all()

    def find_by_role_and_permission(
        self,
        session: Session,
        role_id: str,
        permission_id: str,
        include_deleted: bool = False,
    ) -> Optional[RolePermission]:
        """
        Find specific role-permission assignment.

        Args:
            session: Database session
            role_id: Role UUID
            permission_id: Permission UUID
            include_deleted: Include soft-deleted assignments

        Returns:
            RolePermission if found, None otherwise
        """
        query = session.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )

        if not include_deleted:
            query = query.filter(RolePermission.deleted_at.is_(None))

        return query.first()

