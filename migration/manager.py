"""
Migration manager for database version control.

Handles:
- Auto-creation of migrations table
- Tracking applied migrations
- Applying pending migrations
- Rolling back migrations
- Migration version generation
"""

import glob
import importlib.util
import time
import trace.codes as codes
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy import text

import constants
from database.exceptions import DatabaseMigrationError
from database.session import SessionFactory
from logger import get_logger

logger = get_logger(__name__)


class MigrationManager:
    """
    Manages database migrations with version tracking.

    Features:
    - Auto-creates migrations table on first run
    - Tracks applied migrations
    - Applies pending migrations
    - Rolls back migrations
    - Generates migration versions

    Similar to Laravel Artisan and Goose migration systems.
    """

    def __init__(self):
        """Initialize migration manager."""
        self.session_factory = SessionFactory()
        self.migrations_dir = Path(__file__).parent / "versions"
        self.migrations_table = constants.DB_TABLE_MIGRATIONS

        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_migrations_table_exists(self) -> None:
        """
        Auto-create migrations table if it doesn't exist.

        This is called before any migration operation.
        The migrations table tracks which migrations have been applied.
        """
        engine = self.session_factory.get_write_engine()

        try:
            # Try to query the table
            with engine.connect() as connection:
                connection.execute(
                    text(f"SELECT 1 FROM {self.migrations_table} LIMIT 1")
                )

            logger.info(codes.DB_MIGRATION_TABLE_EXISTS, table=self.migrations_table)

        except Exception:
            # Table doesn't exist, create it
            logger.info(
                codes.DB_CREATING_TABLES,
                table=self.migrations_table,
                msg=constants.MSG_DB_CREATING_TABLES,
            )

            create_table_sql = f"""
                CREATE TABLE {self.migrations_table} (
                    version VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at BIGINT NOT NULL
                )
            """

            try:
                with engine.connect() as connection:
                    connection.execute(text(create_table_sql))
                    connection.commit()

                logger.info(
                    codes.DB_TABLES_CREATED,
                    table=self.migrations_table,
                    msg=constants.MSG_DB_TABLES_CREATED,
                )

            except Exception as e:
                logger.error(codes.DB_MIGRATION_FAILED, error=str(e), exc_info=True)
                raise DatabaseMigrationError(
                    message=constants.ERROR_DB_MIGRATION_TABLE_CREATION_FAILED,
                    details={"table": self.migrations_table},
                    original_error=e,
                ) from e

    def get_applied_migrations(self) -> List[str]:
        """
        Get list of applied migration versions.

        Returns:
            List of migration versions (e.g., ["20250128_000001", "20250128_000002"])

        Raises:
            DatabaseMigrationError: If query fails
        """
        self._ensure_migrations_table_exists()

        logger.info(
            codes.DB_MIGRATION_STATUS_CHECK, msg=constants.MSG_DB_MIGRATION_STATUS_CHECK
        )

        try:
            engine = self.session_factory.get_write_engine()

            with engine.connect() as connection:
                result = connection.execute(
                    text(
                        f"SELECT version FROM {self.migrations_table} ORDER BY version ASC"
                    )
                )
                versions = [row[0] for row in result]

            logger.info(
                codes.DB_MIGRATION_STATUS,
                applied_count=len(versions),
                msg=constants.MSG_DB_MIGRATION_STATUS,
            )

            return versions

        except Exception as e:
            logger.error(
                codes.DB_MIGRATION_FAILED,
                operation="get_applied_migrations",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseMigrationError(
                message=constants.ERROR_DB_MIGRATION_STATUS_CHECK_FAILED,
                details={"operation": "get_applied_migrations"},
                original_error=e,
            ) from e

    def get_pending_migrations(self) -> List[Tuple[str, Path]]:
        """
        Get list of pending (not yet applied) migrations.

        Returns:
            List of tuples: [(version, file_path), ...]

        Raises:
            DatabaseMigrationError: If scanning fails
        """
        applied = set(self.get_applied_migrations())

        # Scan migrations directory
        migration_files = glob.glob(str(self.migrations_dir / "*.py"))
        migration_files = [f for f in migration_files if not f.endswith("__init__.py")]
        migration_files.sort()

        pending = []
        for file_path in migration_files:
            version = Path(file_path).stem  # Get filename without extension
            if version not in applied:
                pending.append((version, Path(file_path)))

        logger.info(
            codes.DB_MIGRATION_PENDING,
            pending_count=len(pending),
            msg=constants.MSG_DB_MIGRATION_PENDING,
        )

        return pending

    def get_all_migrations(self) -> List[Tuple[str, Path, bool]]:
        """
        Get all migrations with their applied status.

        Returns:
            List of tuples: [(version, file_path, is_applied), ...]
        """
        applied = set(self.get_applied_migrations())

        migration_files = glob.glob(str(self.migrations_dir / "*.py"))
        migration_files = [f for f in migration_files if not f.endswith("__init__.py")]
        migration_files.sort()

        all_migrations = []
        for file_path in migration_files:
            version = Path(file_path).stem
            is_applied = version in applied
            all_migrations.append((version, Path(file_path), is_applied))

        return all_migrations

    def apply_migration(self, version: str, file_path: Path) -> None:
        """
        Apply a single migration (run the 'up' function).

        Args:
            version: Migration version identifier
            file_path: Path to migration file

        Raises:
            DatabaseMigrationError: If migration fails
        """
        logger.info(
            codes.DB_MIGRATION_UP_STARTED,
            version=version,
            msg=constants.MSG_DB_MIGRATION_UP_STARTED,
        )

        try:
            # Load migration module dynamically
            spec = importlib.util.spec_from_file_location(version, file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load migration from {file_path}")

            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)

            # Check for 'up' function
            if not hasattr(migration_module, "up"):
                raise AttributeError(f"Migration {version} does not have 'up' function")

            # Execute migration
            engine = self.session_factory.get_write_engine()

            with engine.connect() as connection:
                # Run the up() function
                migration_module.up(connection)

                # Record migration
                current_time = int(time.time() * 1000)
                migration_name = version.split("_", 2)[2] if "_" in version else version

                connection.execute(
                    text(
                        f"""
                        INSERT INTO {self.migrations_table} (version, name, applied_at)
                        VALUES (:version, :name, :applied_at)
                    """
                    ),
                    {
                        "version": version,
                        "name": migration_name,
                        "applied_at": current_time,
                    },
                )

                connection.commit()

            logger.info(
                codes.DB_MIGRATION_UP_COMPLETED,
                version=version,
                msg=constants.MSG_DB_MIGRATION_UP_COMPLETED,
            )

        except Exception as e:
            logger.error(
                codes.DB_MIGRATION_FAILED,
                version=version,
                operation="apply_migration",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseMigrationError(
                message=constants.ERROR_DB_MIGRATION_UP_FAILED,
                details={"version": version},
                original_error=e,
            ) from e

    def rollback_migration(self, version: str, file_path: Path) -> None:
        """
        Rollback a single migration (run the 'down' function).

        Args:
            version: Migration version identifier
            file_path: Path to migration file

        Raises:
            DatabaseMigrationError: If rollback fails
        """
        logger.info(
            codes.DB_MIGRATION_DOWN_STARTED,
            version=version,
            msg=constants.MSG_DB_MIGRATION_DOWN_STARTED,
        )

        try:
            # Load migration module dynamically
            spec = importlib.util.spec_from_file_location(version, file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load migration from {file_path}")

            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)

            # Check for 'down' function
            if not hasattr(migration_module, "down"):
                raise AttributeError(
                    f"Migration {version} does not have 'down' function"
                )

            # Execute rollback
            engine = self.session_factory.get_write_engine()

            with engine.connect() as connection:
                # Run the down() function
                migration_module.down(connection)

                # Remove migration record
                connection.execute(
                    text(
                        f"DELETE FROM {self.migrations_table} WHERE version = :version"
                    ),
                    {"version": version},
                )

                connection.commit()

            logger.info(
                codes.DB_MIGRATION_DOWN_COMPLETED,
                version=version,
                msg=constants.MSG_DB_MIGRATION_DOWN_COMPLETED,
            )

        except Exception as e:
            logger.error(
                codes.DB_MIGRATION_FAILED,
                version=version,
                operation="rollback_migration",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseMigrationError(
                message=constants.ERROR_DB_MIGRATION_DOWN_FAILED,
                details={"version": version},
                original_error=e,
            ) from e

    def generate_version(self, description: str) -> str:
        """
        Generate migration version identifier.

        Format: YYYYMMDD_HHMMSS_description
        Example: 20250128_143022_create_files_table

        Args:
            description: Human-readable migration description

        Returns:
            Migration version string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize description
        safe_description = description.lower().replace(" ", "_").replace("-", "_")
        # Remove non-alphanumeric characters (except underscores)
        safe_description = "".join(
            c for c in safe_description if c.isalnum() or c == "_"
        )

        version = f"{timestamp}_{safe_description}"

        logger.info(
            codes.DB_MIGRATION_GENERATE,
            version=version,
            msg=constants.MSG_MIGRATION_GENERATED,
        )

        return version

    def get_migration_file_path(self, version: str) -> Optional[Path]:
        """
        Get file path for a migration version.

        Args:
            version: Migration version identifier

        Returns:
            Path to migration file, or None if not found
        """
        file_path = self.migrations_dir / f"{version}.py"
        return file_path if file_path.exists() else None
