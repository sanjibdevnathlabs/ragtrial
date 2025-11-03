"""
UserRole service with business logic.

Coordinates between user role repository and business operations.
"""

import time
import uuid
from typing import Dict, List, Optional

import trace.codes as codes
from app.modules.role.repository import RoleRepository
from app.modules.user_role.entity import UserRole
from app.modules.user_role.repository import UserRoleRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class UserRoleService:
    """
    UserRole service for business logic.

    Handles:
    - Assigning roles to users
    - Removing role assignments
    - Retrieving user's roles
    - Checking role expiration
    """

    def __init__(self):
        """Initialize user role service."""
        self.repository = UserRoleRepository()
        self.role_repository = RoleRepository()
        self.session_factory = SessionFactory()

    def get_user_roles(self, user_id: str, include_expired: bool = False) -> List[Dict]:
        """
        Get all roles assigned to a user.

        Args:
            user_id: User UUID
            include_expired: Include expired role assignments

        Returns:
            List of user role dictionaries
        """
        with self.session_factory.get_read_session() as session:
            if include_expired:
                user_roles = self.repository.find_by_user_id(session, user_id)
            else:
                user_roles = self.repository.find_active_by_user_id(session, user_id)

            return [user_role.to_dict() for user_role in user_roles]

    def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[int] = None,
    ) -> Dict:
        """
        Assign role to user.

        Args:
            user_id: User UUID
            role_id: Role UUID
            granted_by: User ID who is granting the role (nullable)
            expires_at: Expiration timestamp in milliseconds (nullable)

        Returns:
            Created user role dictionary

        Raises:
            ValueError: If role doesn't exist
            ValueError: If assignment already exists
        """
        with self.session_factory.get_write_session() as session:
            # Check if role exists
            role = self.role_repository.find_by_id(session, role_id)
            if not role:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="role",
                    role_id=role_id,
                )
                raise ValueError(f"Role with ID '{role_id}' not found")

            # Check if assignment already exists
            existing = self.repository.find_by_user_and_role(
                session, user_id, role_id
            )
            if existing:
                logger.warning(
                    codes.DB_DUPLICATE_ENTRY,
                    entity="user_role",
                    user_id=user_id,
                    role_id=role_id,
                )
                raise ValueError(
                    f"User '{user_id}' already has role '{role.name}' assigned"
                )

            # Create new user role assignment
            current_time_ms = int(time.time() * 1000)
            user_role = UserRole(
                id=str(uuid.uuid4()),
                user_id=user_id,
                role_id=role_id,
                granted_by=granted_by,
                granted_at=current_time_ms,
                expires_at=expires_at,
                created_at=current_time_ms,
                updated_at=current_time_ms,
            )

            created = self.repository.create(session, user_role)
            session.commit()

            logger.info(
                codes.DB_ENTITY_CREATED,
                entity="user_role",
                user_role_id=created.id,
                user_id=user_id,
                role_id=role_id,
                role_name=role.name,
            )

            return created.to_dict()

    def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """
        Remove role assignment from user (soft delete).

        Args:
            user_id: User UUID
            role_id: Role UUID

        Returns:
            True if removed, False if assignment not found
        """
        with self.session_factory.get_write_session() as session:
            user_role = self.repository.find_by_user_and_role(
                session, user_id, role_id
            )
            if not user_role:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="user_role",
                    user_id=user_id,
                    role_id=role_id,
                )
                return False

            self.repository.delete(session, user_role.id)
            session.commit()

            logger.info(
                codes.DB_ENTITY_DELETED,
                entity="user_role",
                user_role_id=user_role.id,
                user_id=user_id,
                role_id=role_id,
            )

            return True

    def check_user_has_role(self, user_id: str, role_name: str) -> bool:
        """
        Check if user has a specific role (by name).

        Args:
            user_id: User UUID
            role_name: Role name

        Returns:
            True if user has the role, False otherwise
        """
        with self.session_factory.get_read_session() as session:
            # Get role by name
            role = self.role_repository.find_by_name(session, role_name)
            if not role:
                return False

            # Check if user has active assignment
            user_roles = self.repository.find_active_by_user_id(session, user_id)
            return any(ur.role_id == role.id for ur in user_roles)

    def get_role_users(self, role_id: str) -> List[Dict]:
        """
        Get all users assigned to a role.

        Args:
            role_id: Role UUID

        Returns:
            List of user role dictionaries
        """
        with self.session_factory.get_read_session() as session:
            user_roles = self.repository.find_by_role_id(session, role_id)
            return [user_role.to_dict() for user_role in user_roles]

