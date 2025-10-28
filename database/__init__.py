"""
Database Infrastructure Module.

This module provides database functionality including:
- Custom exceptions for database errors
- Connection string building
- Session management (read/write split)
- Base models and repositories
- Query logging

Architecture:
- Master-slave database support (read/write split)
- SQLAlchemy ORM integration
- SQL injection prevention
- Parameterized queries
- Multi-database support (SQLite, MySQL, PostgreSQL)
"""

from database.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseSessionError,
    DatabaseQueryError,
    DatabaseMigrationError,
)

__all__ = [
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseSessionError",
    "DatabaseQueryError",
    "DatabaseMigrationError",
]

