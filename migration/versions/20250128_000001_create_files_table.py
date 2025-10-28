"""
Create Files Table

Generated at: 2025-01-28 (Initial Migration)

This migration creates the 'files' table for file metadata storage.

Schema:
- id: VARCHAR(36) - UUID primary key
- filename: VARCHAR(255) - Original filename
- file_path: VARCHAR(512) - Path to stored file
- file_type: VARCHAR(50) - File extension without dot (pdf, txt, md, etc.)
- file_size: BIGINT - File size in bytes
- checksum: VARCHAR(64) - SHA-256 checksum for duplicate detection
- storage_backend: VARCHAR(50) - Storage backend (local, s3)
- indexed: BOOLEAN - Whether file content is indexed
- indexed_at: BIGINT - Timestamp when indexed (milliseconds)
- created_at: BIGINT - Creation timestamp (milliseconds)
- updated_at: BIGINT - Last update timestamp (milliseconds)
- deleted_at: BIGINT - Soft delete timestamp (NULL = active)

Indexes:
- idx_files_checksum: Fast duplicate detection
- idx_files_deleted_at: Filter active vs deleted files
- idx_files_indexed: Query unindexed files
- idx_files_filename: Search by filename

Note: The 'migrations' table is auto-created by the migration system.
"""

from sqlalchemy import text


def up(connection):
    """
    Apply migration - Create files table.
    
    Args:
        connection: SQLAlchemy connection object
    """
    # Create files table
    connection.execute(text("""
        CREATE TABLE files (
            id VARCHAR(36) PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(512) NOT NULL,
            file_type VARCHAR(50) NOT NULL,
            file_size BIGINT NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            storage_backend VARCHAR(50) NOT NULL,
            indexed BOOLEAN NOT NULL DEFAULT FALSE,
            indexed_at BIGINT NULL,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            deleted_at BIGINT NULL,
            CONSTRAINT unique_checksum UNIQUE (checksum)
        )
    """))
    connection.commit()
    
    # Create strategic indexes
    connection.execute(text("CREATE INDEX idx_files_checksum ON files(checksum)"))
    connection.execute(text("CREATE INDEX idx_files_deleted_at ON files(deleted_at)"))
    connection.execute(text("CREATE INDEX idx_files_indexed ON files(indexed)"))
    connection.execute(text("CREATE INDEX idx_files_filename ON files(filename)"))
    connection.commit()


def down(connection):
    """
    Rollback migration - Drop files table.
    
    Args:
        connection: SQLAlchemy connection object
    """
    connection.execute(text("DROP TABLE IF EXISTS files"))
    connection.commit()

