"""
Create Entity Config Table

Generated at: 2025-11-02 (Phase 1: Authentication)

This migration creates the 'entity_config' table for polymorphic configuration storage.

This is a generic key-value configuration table that can store config for any entity
in the system. Each entity can have multiple config rows that together form its
complete configuration/preferences.

Schema:
- id: VARCHAR(36) - UUID primary key
- module_name: VARCHAR(255) - Module name (e.g., "user", "file", "rag")
- entity_type: VARCHAR(255) - Entity type (e.g., "user", "file", "document")
- entity_id: VARCHAR(36) - Entity UUID (links to any table's ID)
- config_key: VARCHAR(255) - Configuration key (e.g., "theme", "language", "notifications")
- config_value: TEXT - Configuration value (can be JSON, string, number)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_config_composite: Composite index (module_name, entity_type, entity_id, config_key)
  Supports fast lookups for:
  - All configs for an entity: WHERE module_name=? AND entity_type=? AND entity_id=?
  - Specific config: WHERE module_name=? AND entity_type=? AND entity_id=? AND config_key=?
- idx_config_entity_id: Fast lookup by entity_id alone
- idx_config_deleted_at: Filter active vs deleted configs

Usage Examples:

User Preferences (multiple rows form complete preferences):
- (module_name="user", entity_type="user", entity_id="user_123", config_key="theme", config_value="dark")
- (module_name="user", entity_type="user", entity_id="user_123", config_key="language", config_value="en")
- (module_name="user", entity_type="user", entity_id="user_123", config_key="upload_mode", config_value="async")
- (module_name="user", entity_type="user", entity_id="user_123", config_key="notifications", config_value='{"email":true,"push":false}')

File Processing Config:
- (module_name="file", entity_type="file", entity_id="file_456", config_key="indexing_strategy", config_value="incremental")
- (module_name="file", entity_type="file", entity_id="file_456", config_key="chunk_size", config_value="500")

RAG Query Preferences:
- (module_name="rag", entity_type="user", entity_id="user_123", config_key="retrieval_k", config_value="10")
- (module_name="rag", entity_type="user", entity_id="user_123", config_key="temperature", config_value="0.7")

Note: This polymorphic design allows flexible configuration storage for any entity
without creating separate preference tables. Each module can define its own config keys.
"""

from sqlalchemy import text


def up(connection):
    """
    Apply migration - Create entity_config table.

    Args:
        connection: SQLAlchemy connection object
    """
    # Create entity_config table
    connection.execute(
        text(
            """
        CREATE TABLE entity_config (
            id VARCHAR(36) PRIMARY KEY,
            module_name VARCHAR(255) NOT NULL,
            entity_type VARCHAR(255) NOT NULL,
            entity_id VARCHAR(36) NOT NULL,
            config_key VARCHAR(255) NOT NULL,
            config_value TEXT NULL,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            deleted_at BIGINT NULL
        )
    """
        )
    )
    connection.commit()

    # Create composite index with prefix lengths (MySQL utf8mb4 key length limit)
    # Using first 100 chars of each varchar column (400 bytes each)
    # Total: 100+100+36+100 = 336 chars = 1344 bytes < 3072 bytes limit
    connection.execute(
        text(
            """
        CREATE INDEX idx_config_composite 
        ON entity_config(module_name(100), entity_type(100), entity_id, config_key(100))
    """
        )
    )

    # Create additional indexes
    connection.execute(
        text("CREATE INDEX idx_config_entity_id ON entity_config(entity_id)")
    )
    connection.execute(
        text("CREATE INDEX idx_config_deleted_at ON entity_config(deleted_at)")
    )
    connection.commit()


def down(connection):
    """
    Rollback migration - Drop entity_config table.

    Args:
        connection: SQLAlchemy connection object
    """
    connection.execute(text("DROP TABLE IF EXISTS entity_config"))
    connection.commit()

