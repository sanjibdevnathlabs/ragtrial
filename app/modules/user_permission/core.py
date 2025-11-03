"""
UserPermission service with business logic.

Coordinates between user permission repository and business operations.
"""

import time
import uuid
from typing import Dict, List, Optional

import trace.codes as codes
from app.modules.permission.repository import PermissionRepository
from app.modules.user_permission.entity import UserPermission
from app.modules.user_permission.repository import UserPermissionRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class UserPermissionService:
    """
    UserPermission service for business logic.

    Handles:
    - Assigning direct permissions to users
    - Removing direct permission assignments
    - Retrieving user's direct permissions
    - Checking permission expiration
    """

    def __init__(self):
        """Initialize user permission service."""
        self.repository = UserPermissionRepository()
        self.permission_repository = PermissionRepository()
        self.session_factory = SessionFactory()

    def get_user_permissions(
        self, user_id: str, include_expired: bool = False
    ) -> List[Dict]:
        """
        Get all direct permissions assigned to a user.

        Args:
            user_id: User UUID
            include_expired: Include expired permission assignments

        Returns:
            List of user permission dictionaries
        """
        with self.session_factory.get_read_session() as session:
            if include_expired:
                user_permissions = self.repository.find_by_user_id(session, user_id)
            else:
                user_permissions = self.repository.find_active_by_user_id(
                    session, user_id
                )

            return [up.to_dict() for up in user_permissions]

    def assign_permission_to_user(
        self,
        user_id: str,
        permission_id: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[int] = None,
    ) -> Dict:
        """
        Assign direct permission to user.

        Args:
            user_id: User UUID
            permission_id: Permission UUID
            granted_by: User ID who is granting the permission (nullable)
            expires_at: Expiration timestamp in milliseconds (nullable)

        Returns:
            Created user permission dictionary

        Raises:
            ValueError: If permission doesn't exist
            ValueError: If assignment already exists
        """
        with self.session_factory.get_write_session() as session:
            # Check if permission exists
            permission = self.permission_repository.find_by_id(session, permission_id)
            if not permission:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="permission",
                    permission_id=permission_id,
                )
                raise ValueError(f"Permission with ID '{permission_id}' not found")

            # Check if assignment already exists
            existing = self.repository.find_by_user_and_permission(
                session, user_id, permission_id
            )
            if existing:
                logger.warning(
                    codes.DB_DUPLICATE_ENTRY,
                    entity="user_permission",
                    user_id=user_id,
                    permission_id=permission_id,
                )
                raise ValueError(
                    f"User '{user_id}' already has permission "
                    f"'{permission.name}' assigned directly"
                )

            # Create new user permission assignment
            current_time_ms = int(time.time() * 1000)
            user_permission = UserPermission(
                id=str(uuid.uuid4()),
                user_id=user_id,
                permission_id=permission_id,
                granted_by=granted_by,
                granted_at=current_time_ms,
                expires_at=expires_at,
                created_at=current_time_ms,
                updated_at=current_time_ms,
            )

            created = self.repository.create(session, user_permission)
            session.commit()

            logger.info(
                codes.DB_ENTITY_CREATED,
                entity="user_permission",
                user_permission_id=created.id,
                user_id=user_id,
                permission_id=permission_id,
                permission_name=permission.name,
            )

            return created.to_dict()

    def remove_permission_from_user(
        self, user_id: str, permission_id: str
    ) -> bool:
        """
        Remove direct permission assignment from user (soft delete).

        Args:
            user_id: User UUID
            permission_id: Permission UUID

        Returns:
            True if removed, False if assignment not found
        """
        with self.session_factory.get_write_session() as session:
            user_permission = self.repository.find_by_user_and_permission(
                session, user_id, permission_id
            )
            if not user_permission:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="user_permission",
                    user_id=user_id,
                    permission_id=permission_id,
                )
                return False

            self.repository.delete(session, user_permission.id)
            session.commit()

            logger.info(
                codes.DB_ENTITY_DELETED,
                entity="user_permission",
                user_permission_id=user_permission.id,
                user_id=user_id,
                permission_id=permission_id,
            )

            return True

    def check_user_has_direct_permission(
        self, user_id: str, permission_name: str
    ) -> bool:
        """
        Check if user has a specific direct permission (by name).

        Args:
            user_id: User UUID
            permission_name: Permission name

        Returns:
            True if user has the direct permission, False otherwise
        """
        with self.session_factory.get_read_session() as session:
            # Get permission by name
            permission = self.permission_repository.find_by_name(
                session, permission_name
            )
            if not permission:
                return False

            # Check if user has active direct assignment
            user_permissions = self.repository.find_active_by_user_id(session, user_id)
            return any(up.permission_id == permission.id for up in user_permissions)

