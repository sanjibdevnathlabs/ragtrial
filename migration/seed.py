"""
Database seed data script

Seeds the database with initial RBAC data:
- Default roles (super_admin, admin, user)
- Permissions for all resources and actions
- Role-permission mappings
- Default super_admin user

This script is idempotent - it checks for existing data before inserting.

Usage:
    python -m migration.seed
    make seed
"""

import sys
import time
import uuid
from typing import Dict, List

from sqlalchemy import text

import constants
import trace.codes as codes
from config import Config
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class SeedData:
    """Database seed data manager."""

    def __init__(self):
        """Initialize seed data manager."""
        self.config = Config()
        self.session_factory = SessionFactory()

    def seed_all(self) -> None:
        """Seed all initial data."""
        logger.info(codes.DB_SEEDING, message="Starting database seeding")

        try:
            # Seed in correct order (dependencies first)
            self.seed_roles()
            self.seed_permissions()
            self.seed_role_permissions()
            self.seed_super_admin_user()
            self.seed_route_permissions()

            logger.info(codes.DB_SEEDED, message="Database seeding completed successfully")
            print("✅ Database seeded successfully!")

        except Exception as e:
            logger.error(
                codes.DB_SEEDING,
                error=str(e),
                message="Database seeding failed",
                exc_info=True,
            )
            print(f"❌ Seeding failed: {e}")
            sys.exit(1)

    def seed_roles(self) -> None:
        """Seed default roles."""
        logger.info(codes.DB_SEEDING, message="Seeding roles")

        roles = [
            {
                "name": "super_admin",
                "description": "Super Administrator with full system access",
            },
            {
                "name": "admin",
                "description": "Administrator with elevated privileges",
            },
            {
                "name": "user",
                "description": "Regular user with basic access",
            },
        ]

        with self.session_factory.get_write_session() as session:
            for role_data in roles:
                # Check if role exists
                result = session.execute(
                    text(
                        f"SELECT id FROM {constants.DB_TABLE_ROLES} "
                        "WHERE name = :name AND deleted_at IS NULL"
                    ),
                    {"name": role_data["name"]},
                )

                if result.fetchone():
                    logger.debug(
                        codes.DB_SEEDING,
                        message=f"Role '{role_data['name']}' already exists, skipping",
                    )
                    print(f"   ⏭️  Role '{role_data['name']}' exists")
                    continue

                # Insert role
                current_time = int(time.time() * 1000)
                session.execute(
                    text(
                        f"INSERT INTO {constants.DB_TABLE_ROLES} "
                        "(id, name, description, created_at, updated_at) "
                        "VALUES (:id, :name, :description, :created_at, :updated_at)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "name": role_data["name"],
                        "description": role_data["description"],
                        "created_at": current_time,
                        "updated_at": current_time,
                    },
                )
                session.commit()
                logger.info(codes.DB_SEEDING, message=f"Role '{role_data['name']}' created")
                print(f"   ✅ Role '{role_data['name']}' created")

    def seed_permissions(self) -> None:
        """Seed default permissions."""
        logger.info(codes.DB_SEEDING, message="Seeding permissions")

        # Define permissions: resource:action
        permissions = [
            # User permissions
            ("user", "read", "View user details"),
            ("user", "write", "Create and update users"),
            ("user", "delete", "Delete users"),
            ("user", "list", "List all users"),
            ("user", "manage", "Full user management"),
            # Role permissions
            ("role", "read", "View role details"),
            ("role", "write", "Create and update roles"),
            ("role", "delete", "Delete roles"),
            ("role", "list", "List all roles"),
            ("role", "manage", "Full role management"),
            # Permission permissions
            ("permission", "read", "View permission details"),
            ("permission", "write", "Create and update permissions"),
            ("permission", "delete", "Delete permissions"),
            ("permission", "list", "List all permissions"),
            ("permission", "manage", "Full permission management"),
            # Rate limit permissions
            ("rate_limit", "read", "View rate limit configs"),
            ("rate_limit", "write", "Create and update rate limits"),
            ("rate_limit", "delete", "Delete rate limits"),
            ("rate_limit", "list", "List all rate limits"),
            ("rate_limit", "manage", "Full rate limit management"),
            # File permissions
            ("file", "read", "View file details"),
            ("file", "write", "Upload and update files"),
            ("file", "delete", "Delete files"),
            ("file", "list", "List all files"),
            ("file", "manage", "Full file management"),
            # Route permission permissions
            ("route_permission", "read", "View route permission configs"),
            ("route_permission", "write", "Create and update route permissions"),
            ("route_permission", "delete", "Delete route permissions"),
            ("route_permission", "list", "List all route permissions"),
            ("route_permission", "manage", "Full route permission management"),
            # System permissions
            ("system", "admin", "System administration"),
            ("system", "config", "System configuration"),
        ]

        with self.session_factory.get_write_session() as session:
            for resource, action, description in permissions:
                permission_name = f"{resource}:{action}"

                # Check if permission exists
                result = session.execute(
                    text(
                        f"SELECT id FROM {constants.DB_TABLE_PERMISSIONS} "
                        "WHERE name = :name AND deleted_at IS NULL"
                    ),
                    {"name": permission_name},
                )

                if result.fetchone():
                    logger.debug(
                        codes.DB_SEEDING,
                        message=f"Permission '{permission_name}' already exists",
                    )
                    continue

                # Insert permission
                current_time = int(time.time() * 1000)
                session.execute(
                    text(
                        f"INSERT INTO {constants.DB_TABLE_PERMISSIONS} "
                        "(id, name, resource, action, description, created_at, updated_at) "
                        "VALUES (:id, :name, :resource, :action, :description, :created_at, :updated_at)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "name": permission_name,
                        "resource": resource,
                        "action": action,
                        "description": description,
                        "created_at": current_time,
                        "updated_at": current_time,
                    },
                )

            session.commit()
            logger.info(
                codes.DB_SEEDING,
                message=f"Created {len(permissions)} permissions",
            )
            print(f"   ✅ Created {len(permissions)} permissions")

    def seed_role_permissions(self) -> None:
        """Seed role-permission mappings."""
        logger.info(codes.DB_SEEDING, message="Seeding role-permission mappings")

        # Define role-permission mappings
        role_permissions_map = {
            "super_admin": "*",  # All permissions
            "admin": [
                "user:read",
                "user:list",
                "user:write",
                "role:read",
                "role:list",
                "permission:read",
                "permission:list",
                "rate_limit:read",
                "rate_limit:write",
                "rate_limit:list",
                "rate_limit:manage",
                "file:read",
                "file:write",
                "file:delete",
                "file:list",
                "file:manage",
                "route_permission:read",
                "route_permission:list",
            ],
            "user": [
                "user:read",  # Can read own user data
                "file:read",  # Can read own files
                "file:write",  # Can upload files
                "file:list",  # Can list own files
            ],
        }

        with self.session_factory.get_write_session() as session:
            for role_name, permissions in role_permissions_map.items():
                # Get role ID
                role_result = session.execute(
                    text(
                        f"SELECT id FROM {constants.DB_TABLE_ROLES} "
                        "WHERE name = :name AND deleted_at IS NULL"
                    ),
                    {"name": role_name},
                )
                role_row = role_result.fetchone()
                if not role_row:
                    logger.warning(
                        codes.DB_SEEDING,
                        message=f"Role '{role_name}' not found, skipping permissions",
                    )
                    continue

                role_id = role_row[0]

                # Get all permissions if wildcard
                if permissions == "*":
                    perm_result = session.execute(
                        text(
                            f"SELECT id FROM {constants.DB_TABLE_PERMISSIONS} "
                            "WHERE deleted_at IS NULL"
                        )
                    )
                    permission_ids = [row[0] for row in perm_result.fetchall()]
                else:
                    # Get specific permission IDs
                    permission_ids = []
                    for perm_name in permissions:
                        perm_result = session.execute(
                            text(
                                f"SELECT id FROM {constants.DB_TABLE_PERMISSIONS} "
                                "WHERE name = :name AND deleted_at IS NULL"
                            ),
                            {"name": perm_name},
                        )
                        perm_row = perm_result.fetchone()
                        if perm_row:
                            permission_ids.append(perm_row[0])

                # Insert role-permission mappings
                current_time = int(time.time() * 1000)
                for permission_id in permission_ids:
                    # Check if mapping exists
                    mapping_result = session.execute(
                        text(
                            f"SELECT id FROM {constants.DB_TABLE_ROLE_PERMISSIONS} "
                            "WHERE role_id = :role_id AND permission_id = :permission_id "
                            "AND deleted_at IS NULL"
                        ),
                        {"role_id": role_id, "permission_id": permission_id},
                    )

                    if mapping_result.fetchone():
                        continue

                    # Insert mapping
                    session.execute(
                        text(
                            f"INSERT INTO {constants.DB_TABLE_ROLE_PERMISSIONS} "
                            "(id, role_id, permission_id, granted_at, created_at, updated_at) "
                            "VALUES (:id, :role_id, :permission_id, :granted_at, :created_at, :updated_at)"
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "role_id": role_id,
                            "permission_id": permission_id,
                            "granted_at": current_time,
                            "created_at": current_time,
                            "updated_at": current_time,
                        },
                    )

                session.commit()
                logger.info(
                    codes.DB_SEEDING,
                    message=f"Mapped {len(permission_ids)} permissions to role '{role_name}'",
                )
                print(f"   ✅ Mapped {len(permission_ids)} permissions to '{role_name}'")

    def seed_super_admin_user(self) -> None:
        """Seed default super admin user."""
        logger.info(codes.DB_SEEDING, message="Seeding super admin user")

        super_admin_email = "admin@ragtrial.com"
        super_admin_password = "Admin@123"  # CHANGE IN PRODUCTION!

        with self.session_factory.get_write_session() as session:
            # Check if super admin exists
            user_result = session.execute(
                text(
                    f"SELECT id FROM {constants.DB_TABLE_USERS} "
                    "WHERE email = :email AND deleted_at IS NULL"
                ),
                {"email": super_admin_email},
            )

            if user_result.fetchone():
                logger.info(
                    codes.DB_SEEDING,
                    message="Super admin user already exists, skipping",
                )
                print("   ⏭️  Super admin user exists")
                return

            # Create super admin user
            # Hash password using bcrypt
            import bcrypt

            password_hash = bcrypt.hashpw(
                super_admin_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # Insert user
            user_id = str(uuid.uuid4())
            current_time = int(time.time() * 1000)

            session.execute(
                text(
                    f"INSERT INTO {constants.DB_TABLE_USERS} "
                    "(id, email, full_name, password_hash, status, is_verified, email_verified_at, created_at, updated_at) "
                    "VALUES (:id, :email, :full_name, :password_hash, :status, :is_verified, :email_verified_at, :created_at, :updated_at)"
                ),
                {
                    "id": user_id,
                    "email": super_admin_email,
                    "full_name": "Super Administrator",
                    "password_hash": password_hash,
                    "status": "active",
                    "is_verified": True,
                    "email_verified_at": current_time,
                    "created_at": current_time,
                    "updated_at": current_time,
                },
            )

            # Get super_admin role ID
            role_result = session.execute(
                text(
                    f"SELECT id FROM {constants.DB_TABLE_ROLES} "
                    "WHERE name = 'super_admin' AND deleted_at IS NULL"
                )
            )
            role_row = role_result.fetchone()

            if role_row:
                role_id = role_row[0]

                # Assign super_admin role to user
                session.execute(
                    text(
                        f"INSERT INTO {constants.DB_TABLE_USER_ROLES} "
                        "(id, user_id, role_id, granted_at, created_at, updated_at) "
                        "VALUES (:id, :user_id, :role_id, :granted_at, :created_at, :updated_at)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "role_id": role_id,
                        "granted_at": current_time,
                        "created_at": current_time,
                        "updated_at": current_time,
                    },
                )

            session.commit()
            logger.info(
                codes.DB_SEEDING,
                message="Super admin user created",
                email=super_admin_email,
            )
            print(f"   ✅ Super admin user created")
            print(f"      📧 Email: {super_admin_email}")
            print(f"      🔑 Password: {super_admin_password}")
            print("      ⚠️  CHANGE PASSWORD IN PRODUCTION!")

    def seed_route_permissions(self) -> None:
        """Seed route permission configurations."""
        logger.info(codes.DB_SEEDING, message="Seeding route permissions")

        route_permissions = [
            # Rate limit management routes
            {
                "route_name": "rate_limits_list",
                "http_method": "GET",
                "route_path": "/api/v1/admin/rate-limits",
                "required_permissions": ["rate_limit:read", "rate_limit:list"],
                "description": "List all rate limit configurations",
            },
            {
                "route_name": "rate_limits_create",
                "http_method": "POST",
                "route_path": "/api/v1/admin/rate-limits",
                "required_permissions": ["rate_limit:write"],
                "description": "Create new rate limit configuration",
            },
            {
                "route_name": "rate_limits_update",
                "http_method": "PUT",
                "route_path": "/api/v1/admin/rate-limits/{id}",
                "required_permissions": ["rate_limit:write"],
                "description": "Update rate limit configuration",
            },
            {
                "route_name": "rate_limits_delete",
                "http_method": "DELETE",
                "route_path": "/api/v1/admin/rate-limits/{id}",
                "required_permissions": ["rate_limit:delete"],
                "description": "Delete rate limit configuration",
            },
        ]

        with self.session_factory.get_write_session() as session:
            for route_data in route_permissions:
                # Check if route permission exists
                result = session.execute(
                    text(
                        f"SELECT id FROM {constants.DB_TABLE_ROUTE_PERMISSIONS} "
                        "WHERE route_name = :route_name AND deleted_at IS NULL"
                    ),
                    {"route_name": route_data["route_name"]},
                )

                if result.fetchone():
                    logger.debug(
                        codes.DB_SEEDING,
                        message=f"Route permission '{route_data['route_name']}' exists",
                    )
                    continue

                # Insert route permission
                import json

                current_time = int(time.time() * 1000)
                session.execute(
                    text(
                        f"INSERT INTO {constants.DB_TABLE_ROUTE_PERMISSIONS} "
                        "(id, route_name, http_method, route_path, required_permissions, "
                        "description, enabled, created_at, updated_at) "
                        "VALUES (:id, :route_name, :http_method, :route_path, "
                        ":required_permissions, :description, :enabled, :created_at, :updated_at)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "route_name": route_data["route_name"],
                        "http_method": route_data["http_method"],
                        "route_path": route_data["route_path"],
                        "required_permissions": json.dumps(
                            route_data["required_permissions"]
                        ),
                        "description": route_data["description"],
                        "enabled": True,
                        "created_at": current_time,
                        "updated_at": current_time,
                    },
                )

            session.commit()
            logger.info(
                codes.DB_SEEDING,
                message=f"Created {len(route_permissions)} route permissions",
            )
            print(f"   ✅ Created {len(route_permissions)} route permissions")


def main():
    """Main entry point for seed script."""
    print("🌱 Starting database seeding...")
    print("")

    seed_data = SeedData()
    seed_data.seed_all()

    print("")
    print("✅ Seeding complete!")


if __name__ == "__main__":
    main()

