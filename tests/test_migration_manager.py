"""
Tests for migration manager.

Tests database migration functionality with proper version tracking.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from database.exceptions import DatabaseMigrationError
from migration.manager import MigrationManager

# ============================================================================
# Test Initialization
# ============================================================================


class TestMigrationManagerInit:
    """Test suite for MigrationManager initialization."""

    def test_init(self):
        """Test manager initialization."""
        manager = MigrationManager()

        assert manager.migrations_table == "migrations"
        assert manager.migrations_dir.name == "versions"
        assert manager.migrations_dir.exists()

    def test_migrations_directory_created(self, tmp_path):
        """Test that migrations directory is created if doesn't exist."""
        with patch.object(Path, "__truediv__", return_value=tmp_path / "new_versions"):
            MigrationManager()

            # Directory should be created
            assert (tmp_path / "new_versions").exists()


# ============================================================================
# Test _ensure_migrations_table_exists
# ============================================================================


class TestEnsureMigrationsTableExists:
    """Test suite for migrations table creation."""

    def test_table_already_exists(self):
        """Test when migrations table already exists."""
        manager = MigrationManager()
        mock_engine = MagicMock()
        mock_connection = MagicMock()

        # Simulate table exists (no exception)
        mock_connection.execute.return_value = None
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            # Should not raise exception
            manager._ensure_migrations_table_exists()

            # Should try to query table
            mock_connection.execute.assert_called_once()

    def test_table_doesnt_exist_creates_it(self):
        """Test table creation when it doesn't exist."""
        manager = MigrationManager()
        mock_engine = MagicMock()
        mock_connection = MagicMock()

        # First call raises exception (table doesn't exist)
        # Second call succeeds (CREATE TABLE)
        mock_connection.execute.side_effect = [Exception("Table doesn't exist"), None]
        mock_connection.commit = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            manager._ensure_migrations_table_exists()

            # Should execute CREATE TABLE
            assert mock_connection.execute.call_count == 2
            mock_connection.commit.assert_called_once()

    def test_table_creation_failure(self):
        """Test error when table creation fails."""
        manager = MigrationManager()
        mock_engine = MagicMock()
        mock_connection = MagicMock()

        # First call fails (table doesn't exist)
        # Second call fails (CREATE TABLE fails)
        mock_connection.execute.side_effect = [
            Exception("Table doesn't exist"),
            Exception("CREATE TABLE failed"),
        ]
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            with pytest.raises(DatabaseMigrationError) as exc_info:
                manager._ensure_migrations_table_exists()

            # Check that the error was raised (actual message is from constant)
            assert exc_info.value is not None


# ============================================================================
# Test get_applied_migrations
# ============================================================================


class TestGetAppliedMigrations:
    """Test suite for getting applied migrations."""

    def test_get_applied_migrations_none(self):
        """Test with no applied migrations."""
        manager = MigrationManager()
        mock_engine = MagicMock()
        mock_connection = MagicMock()

        # First call: check table exists (succeeds)
        # Second call: SELECT migrations (returns empty)
        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter([])
        mock_connection.execute.side_effect = [None, mock_result]
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            versions = manager.get_applied_migrations()

            assert versions == []

    def test_get_applied_migrations_multiple(self):
        """Test with multiple applied migrations."""
        manager = MigrationManager()
        mock_engine = MagicMock()
        mock_connection = MagicMock()

        # First call: check table exists
        # Second call: SELECT migrations
        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter(
            [
                ("20250128_000001_create_files_table",),
                ("20250128_000002_add_index",),
                ("20250128_000003_add_column",),
            ]
        )
        mock_connection.execute.side_effect = [None, mock_result]
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            versions = manager.get_applied_migrations()

            assert len(versions) == 3
            assert versions[0] == "20250128_000001_create_files_table"
            assert versions[1] == "20250128_000002_add_index"
            assert versions[2] == "20250128_000003_add_column"

    def test_get_applied_migrations_failure(self):
        """Test error when querying migrations fails."""
        manager = MigrationManager()
        mock_engine = MagicMock()
        mock_connection = MagicMock()

        # First call: check table exists
        # Second call: SELECT fails
        mock_connection.execute.side_effect = [None, Exception("Query failed")]
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            with pytest.raises(DatabaseMigrationError):
                manager.get_applied_migrations()


# ============================================================================
# Test get_pending_migrations
# ============================================================================


class TestGetPendingMigrations:
    """Test suite for getting pending migrations."""

    def test_get_pending_migrations_all_applied(self, tmp_path):
        """Test when all migrations are already applied."""
        manager = MigrationManager()
        manager.migrations_dir = tmp_path

        # Create migration files
        (tmp_path / "20250128_000001_create_files_table.py").touch()
        (tmp_path / "20250128_000002_add_index.py").touch()

        # Mock all as applied
        with patch.object(
            manager,
            "get_applied_migrations",
            return_value=[
                "20250128_000001_create_files_table",
                "20250128_000002_add_index",
            ],
        ):
            pending = manager.get_pending_migrations()

            assert pending == []

    def test_get_pending_migrations_some_pending(self, tmp_path):
        """Test with some pending migrations."""
        manager = MigrationManager()
        manager.migrations_dir = tmp_path

        # Create migration files
        (tmp_path / "20250128_000001_create_files_table.py").touch()
        (tmp_path / "20250128_000002_add_index.py").touch()
        (tmp_path / "20250128_000003_add_column.py").touch()

        # Only first two applied
        with patch.object(
            manager,
            "get_applied_migrations",
            return_value=[
                "20250128_000001_create_files_table",
                "20250128_000002_add_index",
            ],
        ):
            pending = manager.get_pending_migrations()

            assert len(pending) == 1
            assert pending[0][0] == "20250128_000003_add_column"
            assert pending[0][1].name == "20250128_000003_add_column.py"

    def test_get_pending_migrations_all_pending(self, tmp_path):
        """Test when all migrations are pending."""
        manager = MigrationManager()
        manager.migrations_dir = tmp_path

        # Create migration files
        (tmp_path / "20250128_000001_create_files_table.py").touch()
        (tmp_path / "20250128_000002_add_index.py").touch()

        # None applied
        with patch.object(manager, "get_applied_migrations", return_value=[]):
            pending = manager.get_pending_migrations()

            assert len(pending) == 2
            assert pending[0][0] == "20250128_000001_create_files_table"
            assert pending[1][0] == "20250128_000002_add_index"

    def test_get_pending_migrations_ignores_init(self, tmp_path):
        """Test that __init__.py is ignored."""
        manager = MigrationManager()
        manager.migrations_dir = tmp_path

        # Create files including __init__.py
        (tmp_path / "__init__.py").touch()
        (tmp_path / "20250128_000001_create_files_table.py").touch()

        with patch.object(manager, "get_applied_migrations", return_value=[]):
            pending = manager.get_pending_migrations()

            # Should only return migration file, not __init__.py
            assert len(pending) == 1
            assert pending[0][0] == "20250128_000001_create_files_table"


# ============================================================================
# Test get_all_migrations
# ============================================================================


class TestGetAllMigrations:
    """Test suite for getting all migrations with status."""

    def test_get_all_migrations(self, tmp_path):
        """Test getting all migrations with applied status."""
        manager = MigrationManager()
        manager.migrations_dir = tmp_path

        # Create migration files
        (tmp_path / "20250128_000001_create_files_table.py").touch()
        (tmp_path / "20250128_000002_add_index.py").touch()
        (tmp_path / "20250128_000003_add_column.py").touch()

        # First two applied
        with patch.object(
            manager,
            "get_applied_migrations",
            return_value=[
                "20250128_000001_create_files_table",
                "20250128_000002_add_index",
            ],
        ):
            all_migrations = manager.get_all_migrations()

            assert len(all_migrations) == 3
            assert all_migrations[0][2] is True  # First is applied
            assert all_migrations[1][2] is True  # Second is applied
            assert all_migrations[2][2] is False  # Third is pending


# ============================================================================
# Test apply_migration
# ============================================================================


class TestApplyMigration:
    """Test suite for applying migrations."""

    def test_apply_migration_success(self, tmp_path):
        """Test successful migration application."""
        manager = MigrationManager()

        # Create migration file
        migration_file = tmp_path / "20250128_000001_create_files_table.py"
        migration_file.write_text(
            """
def up(connection):
    from sqlalchemy import text
    connection.execute(text("CREATE TABLE test (id INTEGER)"))
"""
        )

        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_connection.execute = MagicMock()
        mock_connection.commit = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ), patch("time.time", return_value=1706400000.0):

            manager.apply_migration(
                "20250128_000001_create_files_table", migration_file
            )

            # Should commit
            mock_connection.commit.assert_called_once()

            # Should record migration (2 execute calls: up() + INSERT)
            assert mock_connection.execute.call_count >= 1

    def test_apply_migration_no_up_function(self, tmp_path):
        """Test error when migration has no up() function."""
        manager = MigrationManager()

        # Create migration file without up() function
        migration_file = tmp_path / "20250128_000001_bad_migration.py"
        migration_file.write_text("# No up() function")

        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            with pytest.raises(DatabaseMigrationError):
                manager.apply_migration("20250128_000001_bad_migration", migration_file)

    def test_apply_migration_execution_failure(self, tmp_path):
        """Test error when migration execution fails."""
        manager = MigrationManager()

        # Create migration that will fail
        migration_file = tmp_path / "20250128_000001_failing_migration.py"
        migration_file.write_text(
            """
def up(connection):
    raise Exception("Migration execution failed")
"""
        )

        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            with pytest.raises(DatabaseMigrationError):
                manager.apply_migration(
                    "20250128_000001_failing_migration", migration_file
                )


# ============================================================================
# Test rollback_migration
# ============================================================================


class TestRollbackMigration:
    """Test suite for rolling back migrations."""

    def test_rollback_migration_success(self, tmp_path):
        """Test successful migration rollback."""
        manager = MigrationManager()

        # Create migration file
        migration_file = tmp_path / "20250128_000001_create_files_table.py"
        migration_file.write_text(
            """
def down(connection):
    from sqlalchemy import text
    connection.execute(text("DROP TABLE test"))
"""
        )

        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_connection.execute = MagicMock()
        mock_connection.commit = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            manager.rollback_migration(
                "20250128_000001_create_files_table", migration_file
            )

            # Should commit
            mock_connection.commit.assert_called_once()

            # Should execute down() and DELETE
            assert mock_connection.execute.call_count >= 1

    def test_rollback_migration_no_down_function(self, tmp_path):
        """Test error when migration has no down() function."""
        manager = MigrationManager()

        # Create migration file without down() function
        migration_file = tmp_path / "20250128_000001_bad_migration.py"
        migration_file.write_text("# No down() function")

        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            with pytest.raises(DatabaseMigrationError):
                manager.rollback_migration(
                    "20250128_000001_bad_migration", migration_file
                )

    def test_rollback_migration_execution_failure(self, tmp_path):
        """Test error when rollback execution fails."""
        manager = MigrationManager()

        # Create migration that will fail
        migration_file = tmp_path / "20250128_000001_failing_migration.py"
        migration_file.write_text(
            """
def down(connection):
    raise Exception("Rollback execution failed")
"""
        )

        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        with patch.object(
            manager.session_factory, "get_write_engine", return_value=mock_engine
        ):
            with pytest.raises(DatabaseMigrationError):
                manager.rollback_migration(
                    "20250128_000001_failing_migration", migration_file
                )


# ============================================================================
# Test generate_version
# ============================================================================


class TestGenerateVersion:
    """Test suite for version generation."""

    def test_generate_version_format(self):
        """Test version format is correct."""
        manager = MigrationManager()

        with patch("migration.manager.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20250128_143022"

            version = manager.generate_version("create files table")

            assert version.startswith("20250128_143022_")
            assert "create_files_table" in version

    def test_generate_version_sanitizes_description(self):
        """Test that description is sanitized."""
        manager = MigrationManager()

        with patch("migration.manager.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20250128_143022"

            # Test various special characters
            version = manager.generate_version("Create Files Table!")
            assert version == "20250128_143022_create_files_table"

            version = manager.generate_version("add-user-index")
            assert (
                version == "20250128_143022_add_user_index"
            )  # Dashes become underscores

            version = manager.generate_version("fix  multiple   spaces")
            assert (
                version == "20250128_143022_fix__multiple___spaces"
            )  # Multiple spaces become multiple _

    def test_generate_version_removes_special_chars(self):
        """Test that special characters are removed."""
        manager = MigrationManager()

        with patch("migration.manager.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20250128_143022"

            version = manager.generate_version("fix @#$ bug")
            assert (
                version == "20250128_143022_fix__bug"
            )  # Spaces become _, special chars removed


# ============================================================================
# Test get_migration_file_path
# ============================================================================


class TestGetMigrationFilePath:
    """Test suite for getting migration file paths."""

    def test_get_migration_file_path_exists(self, tmp_path):
        """Test getting path for existing migration."""
        manager = MigrationManager()
        manager.migrations_dir = tmp_path

        # Create migration file
        migration_file = tmp_path / "20250128_000001_create_files_table.py"
        migration_file.touch()

        result = manager.get_migration_file_path("20250128_000001_create_files_table")

        assert result == migration_file
        assert result.exists()

    def test_get_migration_file_path_not_exists(self, tmp_path):
        """Test getting path for non-existent migration."""
        manager = MigrationManager()
        manager.migrations_dir = tmp_path

        result = manager.get_migration_file_path("20250128_000001_nonexistent")

        assert result is None
