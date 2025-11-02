"""
RoutePermission service with business logic.

Coordinates between route permission repository and business operations.
"""

import time
import uuid
from typing import Dict, List, Optional

import trace.codes as codes
from app.modules.route_permission.entity import RoutePermission
from app.modules.route_permission.repository import RoutePermissionRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class RoutePermissionService:
    """
    RoutePermission service for business logic.

    Handles:
    - Route permission creation and updates
    - Route permission listing and retrieval
    - Route permission soft deletion
    - Checking required permissions for routes
    """

    def __init__(self):
        """Initialize route permission service."""
        self.repository = RoutePermissionRepository()
        self.session_factory = SessionFactory()

    def get_all_route_permissions(self) -> List[Dict]:
        """
        Get all active route permissions.

        Returns:
            List of route permission dictionaries
        """
        with self.session_factory.get_read_session() as session:
            route_permissions = self.repository.find_all_active(session)
            return [rp.to_dict() for rp in route_permissions]

    def get_route_permission_by_id(
        self, route_permission_id: str
    ) -> Optional[Dict]:
        """
        Get route permission by ID.

        Args:
            route_permission_id: RoutePermission UUID

        Returns:
            RoutePermission dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            route_permission = self.repository.find_by_id(session, route_permission_id)
            return route_permission.to_dict() if route_permission else None

    def get_route_permission_by_name(self, route_name: str) -> Optional[Dict]:
        """
        Get route permission by route name.

        Args:
            route_name: Route name

        Returns:
            RoutePermission dictionary if found, None otherwise
        """
        with self.session_factory.get_read_session() as session:
            route_permission = self.repository.find_by_route_name(session, route_name)
            return route_permission.to_dict() if route_permission else None

    def get_required_permissions(self, route_name: str) -> List[str]:
        """
        Get list of required permissions for a route.

        Args:
            route_name: Route name

        Returns:
            List of permission names, empty list if route not found or disabled
        """
        with self.session_factory.get_read_session() as session:
            route_permission = self.repository.find_by_route_name(session, route_name)
            if not route_permission or not route_permission.is_active():
                return []
            return route_permission.get_required_permissions()

    def create_route_permission(self, data: Dict) -> Dict:
        """
        Create new route permission.

        Args:
            data: Route permission data
                - route_name (str): Unique route name
                - http_method (str): HTTP method
                - route_path (str): API route path
                - required_permissions (List[str]): Permission names required
                - description (str, optional): Description
                - enabled (bool, optional): Enabled status (default True)

        Returns:
            Created route permission dictionary

        Raises:
            ValueError: If route with same name already exists
        """
        with self.session_factory.get_write_session() as session:
            # Check if route already exists
            existing = self.repository.find_by_route_name(session, data["route_name"])
            if existing:
                logger.warning(
                    codes.DB_DUPLICATE_ENTRY,
                    entity="route_permission",
                    route_name=data["route_name"],
                )
                raise ValueError(
                    f"Route permission with name '{data['route_name']}' already exists"
                )

            # Create new route permission
            current_time_ms = int(time.time() * 1000)
            route_permission = RoutePermission(
                id=str(uuid.uuid4()),
                route_name=data["route_name"],
                http_method=data["http_method"],
                route_path=data["route_path"],
                required_permissions="[]",  # Will be set below
                description=data.get("description"),
                enabled=data.get("enabled", True),
                created_at=current_time_ms,
                updated_at=current_time_ms,
            )

            # Set required permissions
            route_permission.set_required_permissions(
                data.get("required_permissions", [])
            )

            created = self.repository.create(session, route_permission)
            session.commit()

            logger.info(
                codes.DB_ENTITY_CREATED,
                entity="route_permission",
                route_permission_id=created.id,
                route_name=data["route_name"],
            )

            return created.to_dict()

    def update_route_permission(
        self, route_permission_id: str, data: Dict
    ) -> Optional[Dict]:
        """
        Update existing route permission.

        Args:
            route_permission_id: RoutePermission UUID
            data: Fields to update

        Returns:
            Updated route permission dictionary if found, None otherwise

        Raises:
            ValueError: If updating route_name to existing route name
        """
        with self.session_factory.get_write_session() as session:
            route_permission = self.repository.find_by_id(session, route_permission_id)
            if not route_permission:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="route_permission",
                    route_permission_id=route_permission_id,
                )
                return None

            # Check if new route_name conflicts
            if (
                "route_name" in data
                and data["route_name"] != route_permission.route_name
            ):
                existing = self.repository.find_by_route_name(session, data["route_name"])
                if existing and existing.id != route_permission_id:
                    raise ValueError(
                        f"Route permission with name '{data['route_name']}' already exists"
                    )

            # Update fields
            if "route_name" in data:
                route_permission.route_name = data["route_name"]
            if "http_method" in data:
                route_permission.http_method = data["http_method"]
            if "route_path" in data:
                route_permission.route_path = data["route_path"]
            if "required_permissions" in data:
                route_permission.set_required_permissions(data["required_permissions"])
            if "description" in data:
                route_permission.description = data["description"]
            if "enabled" in data:
                route_permission.enabled = data["enabled"]

            route_permission.updated_at = int(time.time() * 1000)

            updated = self.repository.update(session, route_permission)
            session.commit()

            logger.info(
                codes.DB_ENTITY_UPDATED,
                entity="route_permission",
                route_permission_id=route_permission_id,
            )

            return updated.to_dict()

    def delete_route_permission(self, route_permission_id: str) -> bool:
        """
        Soft delete route permission.

        Args:
            route_permission_id: RoutePermission UUID

        Returns:
            True if deleted, False if not found
        """
        with self.session_factory.get_write_session() as session:
            route_permission = self.repository.find_by_id(session, route_permission_id)
            if not route_permission:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity="route_permission",
                    route_permission_id=route_permission_id,
                )
                return False

            self.repository.delete(session, route_permission_id)
            session.commit()

            logger.info(
                codes.DB_ENTITY_DELETED,
                entity="route_permission",
                route_permission_id=route_permission_id,
                route_name=route_permission.route_name,
            )

            return True

    def check_route_enabled(self, route_name: str) -> bool:
        """
        Check if a route permission is enabled.

        Args:
            route_name: Route name

        Returns:
            True if route is enabled, False otherwise
        """
        with self.session_factory.get_read_session() as session:
            route_permission = self.repository.find_by_route_name(session, route_name)
            return route_permission.is_active() if route_permission else False

