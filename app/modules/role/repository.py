"""
Role repository with custom query methods.

Extends BaseRepository with role-specific operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.role.entity import Role
from database.base_repository import BaseRepository
from logger import get_logger

logger = get_logger(__name__)


class RoleRepository(BaseRepository[Role]):
    """
    Repository for role operations.

    Extends BaseRepository with role-specific queries:
    - find_by_name()
    - find_all_active()
    """

    def __init__(self):
        """Initialize role repository."""
        super().__init__(Role)

    def find_by_name(
        self, session: Session, name: str, include_deleted: bool = False
    ) -> Optional[Role]:
        """
        Find role by name.

        Args:
            session: Database session
            name: Role name (case-sensitive)
            include_deleted: Include soft-deleted roles

        Returns:
            Role if found, None otherwise
        """
        return self.find_by_field(session, "name", name, include_deleted)

    def find_all_active(self, session: Session) -> List[Role]:
        """
        Find all active (non-deleted) roles.

        Args:
            session: Database session

        Returns:
            List of active roles
        """
        return self.find_all(session, include_deleted=False)

