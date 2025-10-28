"""
Database migration system.

Laravel/Goose-style migration management with:
- Migration generation with timestamps
- Up/down migration support
- Migration status tracking
- Rollback and reset capabilities
"""

from migration.manager import MigrationManager

__all__ = ["MigrationManager"]

