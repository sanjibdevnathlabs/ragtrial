"""
RolePermission service with business logic.

Coordinates between role permission repository and business operations.
"""

import time
import uuid
from typing import Dict, List

import trace.codes as codes
from app.modules.permission.repository import PermissionRepository
from app.modules.role.repository import RoleRepository
from app.modules.role_permission.entity import RolePermission
from app.modules.role_permission.repository import RolePermissionRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class RolePermissionService:
    """
    RolePermission service for business logic.

    Handles:
    - Assigning permissions to roles
    - Removing permission assignments
    - Retrieving role's permissions
    """

    def __init__(self):
        """Initialize role permission service."""
        self.repository = RolePermissionRepository()
        self.role_repository = RoleRepository()
        self.permission_repository = PermissionRepository()
        self.session_factory = SessionFactory()

    def get_role_permissions(self, role_id: str) -> List[Dict]:
        """
        Get all permissions assigned to a role.

        Args:
            role_id: Role UUID

        Returns:
            List of role permission dictionaries
        """
        with self.session_factory.get_read_session() as session:
            role_permissions = self.repository.find_by_role_id(session, role_id)
            return [rp.to_dict() for rp in role_permissions]

    def assign_permission_to_role(
        self,
        role_id: str,
        permission_id: str,
        granted_by: str = None,
    ) -> Dict:
        """
        Assign permission to role.

        Args:
            role_id: Role UUID
            permission_id: Permission UUID
            granted_by: User ID who is granting the permission (nullable)

        Returns:
            Created role permission dictionary

        Raises:
            ValueError: If role doesn't exist
            ValueError: If permission doesn't exist
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
            existing = self.repository.find_by_role_and_permission(
                session, role_id, permission_id
            )
            if existing:
                logger.warning(
                    codes.DB_DUPLICATE_ENTRY,
                    entity="role_permission",
                    role_id=role_id,
                    permission_id=permission_id,
                )
                raise ValueError(
                    f"Role '{role.name}' already has permission "
                    f"'{permission.name}' assigned"
                )

            # Create new role permission assignment
            current_time_ms = int(time.time() * 1000)
            role_permission = RolePermission(
                id=str(uuid.uuid4()),
                role_id=role_id,
                permission_id=permission_id,
                granted_by=granted_by,
                granted_at=current_time_ms,
                created_at=current_time_ms,
                updated_at=current_time_ms,
            )

            created = self.repository.create(session, role_permission)
            session.commit()

            logger.info(
                codes.DB_ENTITY_CREATED,
                entity="role_permission",
                role_permission_id=created.id,
                role_id=role_id,
                role_name=role.name,
                permission_id=permission_id,
                permission_name=permission.name,
            )

            return created.to_dict()

    def remove_permission_from_role(
        self, role_id: str, permission_id: str
    ) -> bool:
        """
        Remove permission assignment from role (soft delete).

        Args:
            role_id: Role UUID
            permission_id: Permission UUID

        Returns:
            True if removed, False if assignment not found
        """
        with self.session_factory.get_write_session() as session:
            role_permission = self.repository.find_by_role_and_permission(
                session, role_id, permission_id
            )
            if not role_permission:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="role_permission",
                    role_id=role_id,
                    permission_id=permission_id,
                )
                return False

            self.repository.delete(session, role_permission.id)
            session.commit()

            logger.info(
                codes.DB_ENTITY_DELETED,
                entity="role_permission",
                role_permission_id=role_permission.id,
                role_id=role_id,
                permission_id=permission_id,
            )

            return True

    def check_role_has_permission(self, role_id: str, permission_name: str) -> bool:
        """
        Check if role has a specific permission (by name).

        Args:
            role_id: Role UUID
            permission_name: Permission name

        Returns:
            True if role has the permission, False otherwise
        """
        with self.session_factory.get_read_session() as session:
            # Get permission by name
            permission = self.permission_repository.find_by_name(
                session, permission_name
            )
            if not permission:
                return False

            # Check if role has permission
            role_permissions = self.repository.find_by_role_id(session, role_id)
            return any(rp.permission_id == permission.id for rp in role_permissions)

