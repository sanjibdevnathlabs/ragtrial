"""
RoutePermission repository with custom query methods.

Extends BaseRepository with route permission operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.route_permission.entity import RoutePermission
from database.base_repository import BaseRepository
from logger import get_logger

logger = get_logger(__name__)


class RoutePermissionRepository(BaseRepository[RoutePermission]):
    """
    Repository for route permission operations.

    Extends BaseRepository with route-permission-specific queries:
    - find_by_route_name()
    - find_by_http_method()
    - find_enabled_routes()
    - find_all_active()
    """

    def __init__(self):
        """Initialize route permission repository."""
        super().__init__(RoutePermission)

    def find_by_route_name(
        self, session: Session, route_name: str, include_deleted: bool = False
    ) -> Optional[RoutePermission]:
        """
        Find route permission by route name.

        Args:
            session: Database session
            route_name: Route name
            include_deleted: Include soft-deleted routes

        Returns:
            RoutePermission if found, None otherwise
        """
        return self.find_by_field(session, "route_name", route_name, include_deleted)

    def find_by_http_method(
        self, session: Session, http_method: str, include_deleted: bool = False
    ) -> List[RoutePermission]:
        """
        Find all route permissions for a specific HTTP method.

        Args:
            session: Database session
            http_method: HTTP method (GET, POST, PUT, DELETE)
            include_deleted: Include soft-deleted routes

        Returns:
            List of route permissions
        """
        query = session.query(RoutePermission).filter(
            RoutePermission.http_method == http_method
        )

        if not include_deleted:
            query = query.filter(RoutePermission.deleted_at.is_(None))

        return query.all()

    def find_enabled_routes(self, session: Session) -> List[RoutePermission]:
        """
        Find all enabled (active) route permissions.

        Args:
            session: Database session

        Returns:
            List of enabled route permissions
        """
        return (
            session.query(RoutePermission)
            .filter(
                RoutePermission.enabled.is_(True),
                RoutePermission.deleted_at.is_(None),
            )
            .all()
        )

    def find_all_active(self, session: Session) -> List[RoutePermission]:
        """
        Find all active (non-deleted) route permissions.

        Args:
            session: Database session

        Returns:
            List of active route permissions
        """
        return self.find_all(session, include_deleted=False)

