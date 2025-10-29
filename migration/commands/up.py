"""
Migration up command.

Usage:
    python -m migration up              # Apply all pending
    python -m migration up --steps 1    # Apply next 1 migration
"""

import trace.codes as codes

from logger import get_logger
from migration.manager import MigrationManager

logger = get_logger(__name__)


def up_command(steps: int = None) -> None:
    """
    Apply pending migrations.

    Args:
        steps: Number of migrations to apply (None = all)
    """
    manager = MigrationManager()

    # Get pending migrations
    pending = manager.get_pending_migrations()

    if not pending:
        print("✅ No pending migrations")
        return

    # Limit if steps specified
    if steps is not None:
        pending = pending[:steps]

    print(f"📋 Found {len(pending)} pending migration(s)")
    print()

    # Apply each migration
    for i, (version, file_path) in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] Applying {version}...", end=" ")

        try:
            manager.apply_migration(version, file_path)
            print("✅ Applied")
        except Exception as e:
            print(f"❌ Failed: {e}")
            logger.error(
                codes.DB_MIGRATION_FAILED, version=version, error=str(e), exc_info=True
            )
            print(f"\n⚠️  Migration failed. Stopping at {version}")
            return

    print()
    print(f"✅ Successfully applied {len(pending)} migration(s)")
