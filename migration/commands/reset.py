"""
Migration reset command.

Usage: python -m migration reset

WARNING: This rolls back ALL migrations and reapplies them.
This is useful for development but dangerous in production.
"""

from migration.manager import MigrationManager
from migration.commands.down import down_command
from migration.commands.up import up_command
from logger import get_logger

logger = get_logger(__name__)


def reset_command(confirm: bool = False) -> None:
    """
    Reset database by rolling back all migrations and reapplying.
    
    Args:
        confirm: If True, skip confirmation prompt
    """
    manager = MigrationManager()
    
    # Get applied migrations count
    applied = manager.get_applied_migrations()
    
    if not applied:
        print("✅ No migrations to reset")
        return
    
    # Confirmation
    if not confirm:
        print()
        print("⚠️  WARNING: This will roll back ALL migrations and reapply them!")
        print(f"   This will affect {len(applied)} migration(s)")
        print()
        response = input("   Type 'yes' to confirm: ")
        if response.lower() != "yes":
            print("❌ Reset cancelled")
            return
    
    print()
    print("🔄 Resetting database...")
    print()
    
    # Step 1: Rollback all
    print("=" * 80)
    print("STEP 1: Rolling back all migrations")
    print("=" * 80)
    down_command(steps=len(applied))
    
    print()
    print("=" * 80)
    print("STEP 2: Reapplying all migrations")
    print("=" * 80)
    
    # Step 2: Reapply all
    up_command()
    
    print()
    print("✅ Database reset complete!")

