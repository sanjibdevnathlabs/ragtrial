"""
Role service with business logic.

Coordinates between role repository and business operations.
"""

import time
import uuid
from typing import Dict, List, Optional

import trace.codes as codes
from app.modules.role.entity import Role
from app.modules.role.repository import RoleRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class RoleService:
    """
    Role service for business logic.

    Handles:
    - Role creation and updates
    - Role listing and retrieval
    - Role soft deletion
    - Role name validation
    """

    def __init__(self):
        """Initialize role service."""
        self.repository = RoleRepository()
        self.session_factory = SessionFactory()

    def get_all_roles(self) -> List[Dict]:
        """
        Get all active roles.

        Returns:
            List of role dictionaries
        """
        with self.session_factory.get_read_session() as session:
            roles = self.repository.find_all_active(session)
            return [role.to_dict() for role in roles]

    def get_role_by_id(self, role_id: str) -> Optional[Dict]:
        """
        Get role by ID.

        Args:
            role_id: Role UUID

        Returns:
            Role dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            role = self.repository.find_by_id(session, role_id)
            return role.to_dict() if role else None

    def get_role_by_name(self, name: str) -> Optional[Dict]:
        """
        Get role by name.

        Args:
            name: Role name (case-sensitive)

        Returns:
            Role dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            role = self.repository.find_by_name(session, name)
            return role.to_dict() if role else None

    def create_role(self, name: str, description: Optional[str] = None) -> Dict:
        """
        Create new role.

        Args:
            name: Role name (must be unique)
            description: Optional description

        Returns:
            Created role dictionary

        Raises:
            ValueError: If role with same name already exists
        """
        # Check if role already exists
        with self.session_factory.get_read_session() as session:
            existing = self.repository.find_by_name(session, name)
            if existing:
                logger.warning(
                    codes.DB_DUPLICATE_ENTRY,
                    entity="role",
                    name=name,
                )
                raise ValueError(f"Role with name '{name}' already exists")

        # Create new role
        role = Role(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000),
        )

        with self.session_factory.get_write_session() as session:
            created = self.repository.create(session, role)
            session.commit()

            logger.info(
                codes.DB_ENTITY_CREATED,
                entity="role",
                role_id=created.id,
                name=name,
            )

            return created.to_dict()

    def update_role(self, role_id: str, data: Dict) -> Optional[Dict]:
        """
        Update existing role.

        Args:
            role_id: Role UUID
            data: Fields to update (name, description)

        Returns:
            Updated role dictionary if found, None otherwise

        Raises:
            ValueError: If updating name to existing role name
        """
        with self.session_factory.get_write_session() as session:
            role = self.repository.find_by_id(session, role_id)
            if not role:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="role",
                    role_id=role_id,
                )
                return None

            # Check if new name conflicts with existing role
            if "name" in data and data["name"] != role.name:
                existing = self.repository.find_by_name(session, data["name"])
                if existing and existing.id != role_id:
                    raise ValueError(f"Role with name '{data['name']}' already exists")

            # Update fields
            if "name" in data:
                role.name = data["name"]
            if "description" in data:
                role.description = data["description"]

            role.updated_at = int(time.time() * 1000)

            updated = self.repository.update(session, role)
            session.commit()

            logger.info(
                codes.DB_ENTITY_UPDATED,
                entity="role",
                role_id=role_id,
            )

            return updated.to_dict()

    def delete_role(self, role_id: str) -> bool:
        """
        Soft delete role.

        Args:
            role_id: Role UUID

        Returns:
            True if deleted, False if not found
        """
        with self.session_factory.get_write_session() as session:
            role = self.repository.find_by_id(session, role_id)
            if not role:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="role",
                    role_id=role_id,
                )
                return False

            self.repository.delete(session, role_id)
            session.commit()

            logger.info(
                codes.DB_ENTITY_DELETED,
                entity="role",
                role_id=role_id,
                name=role.name,
            )

            return True

