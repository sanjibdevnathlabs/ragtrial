"""
Migration status command.

Usage: python -m migration status
"""

from migration.manager import MigrationManager
from logger import get_logger

logger = get_logger(__name__)


def status_command() -> None:
    """Display migration status."""
    manager = MigrationManager()
    
    # Get all migrations
    all_migrations = manager.get_all_migrations()
    
    if not all_migrations:
        print("📋 No migrations found")
        return
    
    # Count applied and pending
    applied_count = sum(1 for _, _, is_applied in all_migrations if is_applied)
    pending_count = len(all_migrations) - applied_count
    
    print()
    print("=" * 80)
    print("  MIGRATION STATUS")
    print("=" * 80)
    print(f"  Total:   {len(all_migrations)}")
    print(f"  Applied: {applied_count}")
    print(f"  Pending: {pending_count}")
    print("=" * 80)
    print()
    
    # Display each migration
    for version, file_path, is_applied in all_migrations:
        status = "✅ Applied" if is_applied else "⏳ Pending"
        print(f"  {status}  {version}")
    
    print()

