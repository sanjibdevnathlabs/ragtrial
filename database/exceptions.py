"""
Custom database exceptions.

This module defines all custom exceptions for database operations, following
a hierarchical structure for proper error handling.

Exception Hierarchy:
    DatabaseError (base)
    ├── DatabaseConnectionError
    ├── DatabaseSessionError
    ├── DatabaseQueryError
    └── DatabaseMigrationError

All exceptions include:
- Custom error messages
- Original exception chaining (from)
- Additional context via details dict
"""

from typing import Any, Dict, Optional

import constants


class DatabaseError(Exception):
    """
    Base exception for all database-related errors.
    
    All custom database exceptions inherit from this class.
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize database error.
        
        Args:
            message: Error message
            details: Additional error context
            original_error: Original exception (for chaining)
        """
        self.message = message
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)


class DatabaseConnectionError(DatabaseError):
    """
    Exception raised when database connection fails.
    
    Examples:
        - Connection refused
        - Authentication failed
        - Network timeout
        - Connection pool exhausted
    """

    def __init__(
        self,
        message: str = constants.ERROR_DB_CONNECTION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize connection error.
        
        Args:
            message: Error message
            details: Connection details (host, port, database, etc.)
            original_error: Original exception (for chaining)
        """
        super().__init__(message, details, original_error)


class DatabaseSessionError(DatabaseError):
    """
    Exception raised when database session operations fail.
    
    Examples:
        - Session creation failed
        - Session already closed
        - Session transaction error
        - Session commit/rollback error
    """

    def __init__(
        self,
        message: str = constants.ERROR_DB_SESSION_CREATION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize session error.
        
        Args:
            message: Error message
            details: Session details (transaction ID, operation, etc.)
            original_error: Original exception (for chaining)
        """
        super().__init__(message, details, original_error)


class DatabaseQueryError(DatabaseError):
    """
    Exception raised when database queries fail.
    
    Examples:
        - Query syntax error
        - Constraint violation
        - Integrity error
        - Foreign key violation
        - Duplicate entry
    """

    def __init__(
        self,
        message: str = constants.ERROR_DB_QUERY_FAILED,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        query: Optional[str] = None
    ):
        """
        Initialize query error.
        
        Args:
            message: Error message
            details: Query details (table, operation, etc.)
            original_error: Original exception (for chaining)
            query: SQL query that failed (for debugging)
        """
        if details is None:
            details = {}
        
        if query:
            details["query"] = query
        
        super().__init__(message, details, original_error)


class DatabaseMigrationError(DatabaseError):
    """
    Exception raised when database migrations fail.
    
    Examples:
        - Migration file not found
        - Migration already applied
        - Migration not applied
        - Migration rollback failed
        - Invalid migration version
    """

    def __init__(
        self,
        message: str = constants.ERROR_MIGRATION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        version: Optional[str] = None,
        migration_name: Optional[str] = None
    ):
        """
        Initialize migration error.
        
        Args:
            message: Error message
            details: Migration details (direction, file, etc.)
            original_error: Original exception (for chaining)
            version: Migration version
            migration_name: Migration name
        """
        if details is None:
            details = {}
        
        if version:
            details["version"] = version
        
        if migration_name:
            details["migration_name"] = migration_name
        
        super().__init__(message, details, original_error)

