"""
Permission service with business logic.

Coordinates between permission repository and business operations.
"""

import time
import uuid
from typing import Dict, List, Optional

import trace.codes as codes
from app.modules.permission.entity import Permission
from app.modules.permission.repository import PermissionRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class PermissionService:
    """
    Permission service for business logic.

    Handles:
    - Permission creation and updates
    - Permission listing and retrieval
    - Permission soft deletion
    - Permission name validation (resource:action format)
    """

    def __init__(self):
        """Initialize permission service."""
        self.repository = PermissionRepository()
        self.session_factory = SessionFactory()

    def get_all_permissions(self) -> List[Dict]:
        """
        Get all active permissions.

        Returns:
            List of permission dictionaries
        """
        with self.session_factory.get_read_session() as session:
            permissions = self.repository.find_all_active(session)
            return [permission.to_dict() for permission in permissions]

    def get_permission_by_id(self, permission_id: str) -> Optional[Dict]:
        """
        Get permission by ID.

        Args:
            permission_id: Permission UUID

        Returns:
            Permission dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            permission = self.repository.find_by_id(session, permission_id)
            return permission.to_dict() if permission else None

    def get_permission_by_name(self, name: str) -> Optional[Dict]:
        """
        Get permission by name.

        Args:
            name: Permission name (format: 'resource:action')

        Returns:
            Permission dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            permission = self.repository.find_by_name(session, name)
            return permission.to_dict() if permission else None

    def get_permissions_by_resource(self, resource: str) -> List[Dict]:
        """
        Get all permissions for a resource.

        Args:
            resource: Resource type (e.g., 'user', 'file')

        Returns:
            List of permission dictionaries
        """
        with self.session_factory.get_read_session() as session:
            permissions = self.repository.find_by_resource(session, resource)
            return [permission.to_dict() for permission in permissions]

    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Create new permission.

        Args:
            name: Permission name (must be unique, format: 'resource:action')
            resource: Resource type
            action: Action type
            description: Optional description

        Returns:
            Created permission dictionary

        Raises:
            ValueError: If permission with same name already exists
            ValueError: If name format is invalid
        """
        # Validate name format
        if ":" not in name:
            raise ValueError(
                f"Invalid permission name format: '{name}'. Expected 'resource:action'"
            )

        # Check if permission already exists
        with self.session_factory.get_read_session() as session:
            existing = self.repository.find_by_name(session, name)
            if existing:
                logger.warning(
                    codes.DB_DUPLICATE_ENTRY,
                    entity="permission",
                    name=name,
                )
                raise ValueError(f"Permission with name '{name}' already exists")

        # Create new permission
        permission = Permission(
            id=str(uuid.uuid4()),
            name=name,
            resource=resource,
            action=action,
            description=description,
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000),
        )

        with self.session_factory.get_write_session() as session:
            created = self.repository.create(session, permission)
            session.commit()

            logger.info(
                codes.DB_ENTITY_CREATED,
                entity="permission",
                permission_id=created.id,
                name=name,
            )

            return created.to_dict()

    def update_permission(self, permission_id: str, data: Dict) -> Optional[Dict]:
        """
        Update existing permission.

        Args:
            permission_id: Permission UUID
            data: Fields to update (name, resource, action, description)

        Returns:
            Updated permission dictionary if found, None otherwise

        Raises:
            ValueError: If updating name to existing permission name
            ValueError: If name format is invalid
        """
        with self.session_factory.get_write_session() as session:
            permission = self.repository.find_by_id(session, permission_id)
            if not permission:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="permission",
                    permission_id=permission_id,
                )
                return None

            # Validate name format if updating name
            if "name" in data and ":" not in data["name"]:
                raise ValueError(
                    f"Invalid permission name format: '{data['name']}'. "
                    "Expected 'resource:action'"
                )

            # Check if new name conflicts with existing permission
            if "name" in data and data["name"] != permission.name:
                existing = self.repository.find_by_name(session, data["name"])
                if existing and existing.id != permission_id:
                    raise ValueError(
                        f"Permission with name '{data['name']}' already exists"
                    )

            # Update fields
            if "name" in data:
                permission.name = data["name"]
            if "resource" in data:
                permission.resource = data["resource"]
            if "action" in data:
                permission.action = data["action"]
            if "description" in data:
                permission.description = data["description"]

            permission.updated_at = int(time.time() * 1000)

            updated = self.repository.update(session, permission)
            session.commit()

            logger.info(
                codes.DB_ENTITY_UPDATED,
                entity="permission",
                permission_id=permission_id,
            )

            return updated.to_dict()

    def delete_permission(self, permission_id: str) -> bool:
        """
        Soft delete permission.

        Args:
            permission_id: Permission UUID

        Returns:
            True if deleted, False if not found
        """
        with self.session_factory.get_write_session() as session:
            permission = self.repository.find_by_id(session, permission_id)
            if not permission:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="permission",
                    permission_id=permission_id,
                )
                return False

            self.repository.delete(session, permission_id)
            session.commit()

            logger.info(
                codes.DB_ENTITY_DELETED,
                entity="permission",
                permission_id=permission_id,
                name=permission.name,
            )

            return True

