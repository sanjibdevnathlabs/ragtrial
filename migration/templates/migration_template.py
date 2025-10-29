"""
Template for generated migration files.

Usage:
    Replace {{DESCRIPTION}} with migration description
    Implement up() and down() functions
"""

MIGRATION_TEMPLATE = '''"""
{{DESCRIPTION}}

Generated at: {{TIMESTAMP}}
"""


def up(connection):
    """
    Apply migration (forward).

    Args:
        connection: SQLAlchemy connection object

    Example:
        connection.execute("""
            CREATE TABLE users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                created_at BIGINT NOT NULL
            )
        """)
    """
    # TODO: Implement forward migration
    pass


def down(connection):
    """
    Rollback migration (backward).

    Args:
        connection: SQLAlchemy connection object

    Example:
        connection.execute("DROP TABLE IF EXISTS users")
    """
    # TODO: Implement rollback migration
    pass
'''


def get_template() -> str:
    """Get migration template string."""
    return MIGRATION_TEMPLATE
