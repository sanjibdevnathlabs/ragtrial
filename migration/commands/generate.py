"""
Migration generation command.

Usage: python -m migration generate create_users_table
"""

import trace.codes as codes
from datetime import datetime

from logger import get_logger
from migration.manager import MigrationManager
from migration.templates.migration_template import get_template

logger = get_logger(__name__)


def generate_command(description: str) -> str:
    """
    Generate a new migration file.

    Args:
        description: Human-readable migration description

    Returns:
        Path to generated migration file

    Example:
        >>> generate_command("create_users_table")
        'migration/versions/20250128_143022_create_users_table.py'
    """
    manager = MigrationManager()

    # Generate version
    version = manager.generate_version(description)

    # Get template
    template = get_template()

    # Replace placeholders
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = template.replace("{{DESCRIPTION}}", description.replace("_", " ").title())
    content = content.replace("{{TIMESTAMP}}", timestamp)

    # Write file
    file_path = manager.migrations_dir / f"{version}.py"
    file_path.write_text(content)

    logger.info(codes.DB_MIGRATION_GENERATED, version=version, path=str(file_path))

    print(f"✅ Migration generated: {file_path}")
    print(f"📝 Version: {version}")
    print("\nNext steps:")
    print(f"1. Edit {file_path}")
    print("2. Implement up() function")
    print("3. Implement down() function")
    print("4. Run: python -m migration up")

    return str(file_path)
