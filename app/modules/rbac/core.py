"""
RBAC Permission Service - Orchestration layer.

Combines all RBAC modules to provide unified permission checking.
"""

from typing import Dict, List, Set

import trace.codes as codes
from app.modules.permission.repository import PermissionRepository
from app.modules.role.repository import RoleRepository
from app.modules.role_permission.repository import RolePermissionRepository
from app.modules.user_permission.repository import UserPermissionRepository
from app.modules.user_role.repository import UserRoleRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class PermissionService:
    """
    RBAC Permission Service - Main orchestration layer.

    Combines:
    - Direct user permissions (user_permission module)
    - Role-based permissions (user_role + role_permission modules)

    Handles:
    - Permission checking with expiration logic
    - Combined permission retrieval
    - Role and permission name resolution
    """

    def __init__(self):
        """Initialize permission service with all RBAC repositories."""
        self.permission_repo = PermissionRepository()
        self.role_repo = RoleRepository()
        self.user_role_repo = UserRoleRepository()
        self.role_permission_repo = RolePermissionRepository()
        self.user_permission_repo = UserPermissionRepository()
        self.session_factory = SessionFactory()

    def user_has_permission(self, user_id: str, permission_name: str) -> bool:
        """
        Check if user has a specific permission.

        Checks both:
        1. Direct user permissions
        2. Permissions via user's active roles

        Args:
            user_id: User UUID
            permission_name: Permission name (e.g., 'user:read')

        Returns:
            True if user has permission, False otherwise
        """
        with self.session_factory.get_read_session() as session:
            # Get permission by name
            permission = self.permission_repo.find_by_name(session, permission_name)
            if not permission:
                logger.debug(
                    codes.RBAC_PERMISSION_NOT_FOUND,
                    user_id=user_id,
                    permission_name=permission_name,
                )
                return False

            permission_id = permission.id

            # Check 1: Direct user permissions (active, non-expired)
            user_permissions = self.user_permission_repo.find_active_by_user_id(
                session, user_id
            )
            if any(up.permission_id == permission_id for up in user_permissions):
                logger.debug(
                    codes.RBAC_PERMISSION_GRANTED_DIRECT,
                    user_id=user_id,
                    permission_name=permission_name,
                )
                return True

            # Check 2: Permissions via roles
            # Get user's active roles
            user_roles = self.user_role_repo.find_active_by_user_id(session, user_id)
            if not user_roles:
                logger.debug(
                    codes.RBAC_PERMISSION_DENIED,
                    user_id=user_id,
                    permission_name=permission_name,
                    reason="no_active_roles",
                )
                return False

            # Check each role's permissions
            for user_role in user_roles:
                role_permissions = self.role_permission_repo.find_by_role_id(
                    session, user_role.role_id
                )
                if any(rp.permission_id == permission_id for rp in role_permissions):
                    # Get role name for logging
                    role = self.role_repo.find_by_id(session, user_role.role_id)
                    logger.debug(
                        codes.RBAC_PERMISSION_GRANTED_VIA_ROLE,
                        user_id=user_id,
                        permission_name=permission_name,
                        role_name=role.name if role else user_role.role_id,
                    )
                    return True

            logger.debug(
                codes.RBAC_PERMISSION_DENIED,
                user_id=user_id,
                permission_name=permission_name,
                reason="not_found_in_roles_or_direct",
            )
            return False

    def get_all_user_permissions(self, user_id: str) -> List[str]:
        """
        Get all effective permissions for a user.

        Combines:
        - Direct user permissions
        - Permissions from all user's active roles

        Args:
            user_id: User UUID

        Returns:
            List of unique permission names
        """
        with self.session_factory.get_read_session() as session:
            permission_ids: Set[str] = set()

            # Collect direct user permissions
            user_permissions = self.user_permission_repo.find_active_by_user_id(
                session, user_id
            )
            permission_ids.update(up.permission_id for up in user_permissions)

            # Collect permissions from roles
            user_roles = self.user_role_repo.find_active_by_user_id(session, user_id)
            for user_role in user_roles:
                role_permissions = self.role_permission_repo.find_by_role_id(
                    session, user_role.role_id
                )
                permission_ids.update(rp.permission_id for rp in role_permissions)

            # Convert permission IDs to names
            permission_names = []
            for permission_id in permission_ids:
                permission = self.permission_repo.find_by_id(session, permission_id)
                if permission:
                    permission_names.append(permission.name)

            logger.debug(
                codes.RBAC_USER_PERMISSIONS_RETRIEVED,
                user_id=user_id,
                count=len(permission_names),
            )

            return sorted(permission_names)

    def get_user_effective_roles(self, user_id: str) -> List[Dict]:
        """
        Get user's active (non-expired) roles with details.

        Args:
            user_id: User UUID

        Returns:
            List of role dictionaries with role details
        """
        with self.session_factory.get_read_session() as session:
            user_roles = self.user_role_repo.find_active_by_user_id(session, user_id)

            roles = []
            for user_role in user_roles:
                role = self.role_repo.find_by_id(session, user_role.role_id)
                if role:
                    roles.append(
                        {
                            "role_id": role.id,
                            "role_name": role.name,
                            "description": role.description,
                            "granted_at": user_role.granted_at,
                            "expires_at": user_role.expires_at,
                        }
                    )

            logger.debug(
                codes.RBAC_USER_ROLES_RETRIEVED,
                user_id=user_id,
                count=len(roles),
            )

            return roles

    def check_multiple_permissions(
        self, user_id: str, permission_names: List[str]
    ) -> Dict[str, bool]:
        """
        Check multiple permissions at once (batch operation).

        Args:
            user_id: User UUID
            permission_names: List of permission names to check

        Returns:
            Dictionary mapping permission name to boolean (has permission)
        """
        results = {}
        for permission_name in permission_names:
            results[permission_name] = self.user_has_permission(
                user_id, permission_name
            )

        logger.debug(
            codes.RBAC_BATCH_PERMISSION_CHECK,
            user_id=user_id,
            total=len(permission_names),
            granted=sum(1 for v in results.values() if v),
        )

        return results

    def user_has_any_permission(
        self, user_id: str, permission_names: List[str]
    ) -> bool:
        """
        Check if user has ANY of the given permissions (OR logic).

        Args:
            user_id: User UUID
            permission_names: List of permission names

        Returns:
            True if user has at least one permission
        """
        for permission_name in permission_names:
            if self.user_has_permission(user_id, permission_name):
                logger.debug(
                    codes.RBAC_ANY_PERMISSION_GRANTED,
                    user_id=user_id,
                    granted_permission=permission_name,
                )
                return True

        logger.debug(
            codes.RBAC_PERMISSION_DENIED,
            user_id=user_id,
            reason="none_of_required_permissions",
            required=permission_names,
        )
        return False

    def user_has_all_permissions(
        self, user_id: str, permission_names: List[str]
    ) -> bool:
        """
        Check if user has ALL of the given permissions (AND logic).

        Args:
            user_id: User UUID
            permission_names: List of permission names

        Returns:
            True if user has all permissions
        """
        for permission_name in permission_names:
            if not self.user_has_permission(user_id, permission_name):
                logger.debug(
                    codes.RBAC_PERMISSION_DENIED,
                    user_id=user_id,
                    reason="missing_required_permission",
                    missing_permission=permission_name,
                )
                return False

        logger.debug(
            codes.RBAC_ALL_PERMISSIONS_GRANTED,
            user_id=user_id,
            count=len(permission_names),
        )
        return True

