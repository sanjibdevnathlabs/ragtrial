"""
User service for CRUD operations.

Single responsibility: User entity management only.
"""

import trace.codes as codes
from typing import Dict, List, Optional

import constants
from app.modules.user.entity import User
from app.modules.user.repository import UserRepository
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class UserService:
    """
    User CRUD service.

    Responsibilities:
    - Create user entity
    - Read user data
    - Update user profile
    - Manage user status
    - Soft delete users
    """

    def __init__(self):
        """Initialize user service."""
        self.repository = UserRepository()
        self.session_factory = SessionFactory()

    def create_user(
        self,
        email: str,
        full_name: str,
        password_hash: Optional[str] = None,
    ) -> Dict:
        """
        Create new user entity.

        Args:
            email: User email (unique)
            full_name: User full name
            password_hash: Hashed password (optional for OAuth users)

        Returns:
            Created user dictionary

        Raises:
            ValueError: If email already exists
        """
        logger.info(codes.DB_REPOSITORY_STARTED, operation="create_user", email=email)

        with self.session_factory.get_read_session() as session:
            if self.repository.find_by_email(session, email):
                raise ValueError(f"User with email {email} already exists")

        user = User(
            id=User.generate_id(),
            email=email.lower().strip(),
            full_name=full_name.strip(),
            password_hash=password_hash,
            is_verified=False,
            status=constants.USER_STATUS_ACTIVE,
        )

        with self.session_factory.get_write_session() as session:
            created = self.repository.create(session, user)

        logger.info(
            codes.DB_REPOSITORY_COMPLETED,
            operation="create_user",
            user_id=created.id,
        )

        return created.to_dict()

    def get_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        with self.session_factory.get_read_session() as session:
            user = self.repository.find_by_id(session, user_id)
            return user.to_dict() if user else None

    def get_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        with self.session_factory.get_read_session() as session:
            user = self.repository.find_by_email(session, email.lower().strip())
            return user.to_dict() if user else None

    def update_profile(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Update user profile fields.

        Args:
            user_id: User ID
            full_name: New full name
            avatar_url: New avatar URL

        Returns:
            Updated user dictionary or None if not found
        """
        with self.session_factory.get_write_session() as session:
            user = self.repository.find_by_id(session, user_id)

            if not user:
                logger.warning(codes.DB_ENTITY_NOT_FOUND, user_id=user_id)
                return None

            if full_name is not None:
                user.full_name = full_name.strip()

            if avatar_url is not None:
                user.avatar_url = avatar_url

            updated = self.repository.update(session, user)

        return updated.to_dict()

    def mark_verified(self, user_id: str) -> bool:
        """Mark user email as verified."""
        with self.session_factory.get_write_session() as session:
            return self.repository.mark_as_verified(session, user_id)

    def suspend(self, user_id: str) -> bool:
        """Suspend user account."""
        with self.session_factory.get_write_session() as session:
            return self.repository.suspend_user(session, user_id)

    def activate(self, user_id: str) -> bool:
        """Activate user account."""
        with self.session_factory.get_write_session() as session:
            return self.repository.activate_user(session, user_id)

    def soft_delete(self, user_id: str) -> bool:
        """Soft delete user."""
        with self.session_factory.get_write_session() as session:
            return self.repository.soft_delete(session, user_id)

    def list_by_status(self, status: str) -> List[Dict]:
        """List users by status."""
        with self.session_factory.get_read_session() as session:
            users = self.repository.find_by_status(session, status)
            return [u.to_dict() for u in users]

    def count_by_status(self, status: str) -> int:
        """Count users by status."""
        with self.session_factory.get_read_session() as session:
            return self.repository.count_by_status(session, status)

    def get_all_users(self) -> List[Dict]:
        """Get all active users."""
        with self.session_factory.get_read_session() as session:
            users = self.repository.find_all(session, include_deleted=False)
            return [u.to_dict() for u in users]

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID (alias for get_by_id)."""
        return self.get_by_id(user_id)

    def create_user_admin(
        self, email: str, full_name: str, password: str, status: str = "active"
    ) -> Dict:
        """
        Create user (admin operation with password hashing).

        Args:
            email: User email
            full_name: Full name
            password: Plain text password (will be hashed)
            status: User status

        Returns:
            Created user dictionary
        """
        import bcrypt

        # Hash password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

        # Create user with hashed password
        user_dict = self.create_user(email, full_name, password_hash)

        # Update status if different from active
        if status != "active":
            user_dict = self.update_user(
                user_dict["id"], {"status": status}
            )

        return user_dict

    def update_user(self, user_id: str, data: Dict) -> Optional[Dict]:
        """
        Update user fields (admin operation).

        Args:
            user_id: User ID
            data: Fields to update (full_name, status, etc.)

        Returns:
            Updated user dictionary or None if not found
        """
        with self.session_factory.get_write_session() as session:
            user = self.repository.find_by_id(session, user_id)

            if not user:
                logger.warning(codes.DB_ENTITY_NOT_FOUND, user_id=user_id)
                return None

            # Update fields
            if "full_name" in data:
                user.full_name = data["full_name"].strip()
            if "status" in data:
                user.status = data["status"]
            if "avatar_url" in data:
                user.avatar_url = data["avatar_url"]

            updated = self.repository.update(session, user)

        return updated.to_dict()

    def delete_user(self, user_id: str) -> bool:
        """Soft delete user (alias for soft_delete)."""
        return self.soft_delete(user_id)

