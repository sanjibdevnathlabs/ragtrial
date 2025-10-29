"""
Base SQLAlchemy model with common fields.

All database models should inherit from BaseModel to get:
- id (VARCHAR primary key for UUID)
- created_at (BIGINT timestamp in milliseconds)
- updated_at (BIGINT timestamp in milliseconds)
- deleted_at (BIGINT timestamp in milliseconds, NULL for active records)
- to_dict() method for serialization
- __repr__() for debugging
"""

import time
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import declarative_base, declared_attr

import constants

# SQLAlchemy declarative base
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model for all database entities.

    Provides common fields and utility methods that all models inherit.

    Fields:
        id: VARCHAR(36) primary key (UUID)
        created_at: BIGINT timestamp in milliseconds
        updated_at: BIGINT timestamp in milliseconds
        deleted_at: BIGINT timestamp in milliseconds (NULL = active, soft delete)

    Methods:
        to_dict(): Convert model to dictionary
        __repr__(): String representation for debugging
    """

    __abstract__ = True  # This is an abstract base class

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Auto-generate table name from class name.

        Example: UserModel -> user_model
        """
        return cls.__name__.lower()

    # Primary key (UUID generated in Python)
    id = Column(String(36), primary_key=True)

    # Timestamps (all in milliseconds since epoch)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)
    deleted_at = Column(BigInteger, nullable=True, default=None)

    def __init__(self, **kwargs):
        """
        Initialize model with automatic timestamp management.

        Args:
            **kwargs: Model fields
        """
        # Set timestamps if not provided
        current_time = self._get_current_timestamp()

        if constants.DB_COLUMN_CREATED_AT not in kwargs:
            kwargs[constants.DB_COLUMN_CREATED_AT] = current_time

        if constants.DB_COLUMN_UPDATED_AT not in kwargs:
            kwargs[constants.DB_COLUMN_UPDATED_AT] = current_time

        super().__init__(**kwargs)

    @staticmethod
    def _get_current_timestamp() -> int:
        """
        Get current timestamp in milliseconds.

        Returns:
            Current Unix timestamp in milliseconds
        """
        return int(time.time() * 1000)

    def update_timestamp(self) -> None:
        """
        Update the updated_at timestamp to current time.

        Call this before saving updated records.
        """
        self.updated_at = self._get_current_timestamp()

    def soft_delete(self) -> None:
        """
        Soft delete this record by setting deleted_at timestamp.

        The record remains in the database but is filtered from queries.
        """
        if self.deleted_at is None:
            self.deleted_at = self._get_current_timestamp()
            self.update_timestamp()

    def restore(self) -> None:
        """
        Restore a soft-deleted record by clearing deleted_at.
        """
        if self.deleted_at is not None:
            self.deleted_at = None
            self.update_timestamp()

    def is_deleted(self) -> bool:
        """
        Check if this record is soft-deleted.

        Returns:
            True if deleted_at is set, False otherwise
        """
        return self.deleted_at is not None

    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Useful for JSON serialization and API responses.

        Args:
            exclude: List of field names to exclude from dictionary

        Returns:
            Dictionary representation of model
        """
        exclude = exclude or []

        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                result[column.name] = value

        return result

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Returns:
            Human-readable string representation
        """
        class_name = self.__class__.__name__

        # Show ID and deleted status
        if hasattr(self, constants.DB_COLUMN_ID):
            id_value = getattr(self, constants.DB_COLUMN_ID)
            deleted = " (DELETED)" if self.is_deleted() else ""
            return f"<{class_name}(id={id_value!r}){deleted}>"

        return f"<{class_name}>"

    def __str__(self) -> str:
        """
        User-friendly string representation.

        Returns:
            String representation for display
        """
        return self.__repr__()
