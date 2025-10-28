"""
Migration down command.

Usage:
    python -m migration down              # Rollback last migration
    python -m migration down --steps 2    # Rollback last 2 migrations
"""

from migration.manager import MigrationManager
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)


def down_command(steps: int = 1) -> None:
    """
    Rollback applied migrations.
    
    Args:
        steps: Number of migrations to rollback (default: 1)
    """
    manager = MigrationManager()
    
    # Get applied migrations
    applied = manager.get_applied_migrations()
    
    if not applied:
        print("✅ No migrations to rollback")
        return
    
    # Get migrations to rollback (most recent first)
    to_rollback = applied[-steps:]
    to_rollback.reverse()
    
    print(f"📋 Rolling back {len(to_rollback)} migration(s)")
    print()
    
    # Rollback each migration
    for i, version in enumerate(to_rollback, 1):
        file_path = manager.get_migration_file_path(version)
        if file_path is None:
            print(f"❌ Migration file not found for {version}")
            continue
        
        print(f"[{i}/{len(to_rollback)}] Rolling back {version}...", end=" ")
        
        try:
            manager.rollback_migration(version, file_path)
            print("✅ Rolled back")
        except Exception as e:
            print(f"❌ Failed: {e}")
            logger.error(
                codes.DB_MIGRATION_FAILED,
                version=version,
                error=str(e),
                exc_info=True
            )
            print(f"\n⚠️  Rollback failed. Stopping at {version}")
            return
    
    print()
    print(f"✅ Successfully rolled back {len(to_rollback)} migration(s)")

