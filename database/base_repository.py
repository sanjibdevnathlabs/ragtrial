"""
Base repository pattern with SQL injection-safe CRUD operations.

All entity repositories should inherit from BaseRepository to get:
- find_by_id() - Find by primary key
- find_all() - Get all records (excluding soft deleted)
- find_by_field() - Find by any field with parameterized queries
- create() - Insert new record
- update() - Update existing record
- delete() - Soft delete record
- hard_delete() - Permanently remove record
- count() - Count records
- exists() - Check existence

All queries use parameterized statements to prevent SQL injection.
"""

import trace.codes as codes
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

import constants
from database.base_model import BaseModel
from database.exceptions import DatabaseQueryError
from logger import get_logger

logger = get_logger(__name__)

# Generic type for model class
ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository for CRUD operations.

    Provides SQL injection-safe database operations using parameterized queries.
    All methods automatically exclude soft-deleted records unless explicitly included.

    Type Parameters:
        ModelType: The SQLAlchemy model class this repository manages

    Example:
        class UserRepository(BaseRepository[User]):
            def find_by_email(self, session: Session, email: str) -> Optional[User]:
                return self.find_by_field(session, "email", email)
    """

    def __init__(self, model_class: Type[ModelType]):
        """
        Initialize repository with model class.

        Args:
            model_class: The SQLAlchemy model class to manage
        """
        self.model_class = model_class

    def find_by_id(
        self, session: Session, entity_id: str, include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Find entity by ID (primary key).

        Uses parameterized query to prevent SQL injection.

        Args:
            session: Database session
            entity_id: Primary key value
            include_deleted: If True, include soft-deleted records

        Returns:
            Entity if found, None otherwise

        Raises:
            DatabaseQueryError: If query execution fails
        """
        try:
            logger.info(
                codes.DB_QUERY_STARTED,
                operation="find_by_id",
                model=self.model_class.__name__,
                entity_id=entity_id,
            )

            query = session.query(self.model_class).filter(
                self.model_class.id == entity_id  # Parameterized
            )

            if not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            result = query.first()

            logger.info(
                codes.DB_QUERY_COMPLETED,
                operation="find_by_id",
                found=result is not None,
            )

            return result

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="find_by_id",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query=f"find_by_id({entity_id})",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def find_all(
        self,
        session: Session,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> List[ModelType]:
        """
        Find all entities.

        Args:
            session: Database session
            include_deleted: If True, include soft-deleted records
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Field name to order by
            order_desc: If True, order descending

        Returns:
            List of entities

        Raises:
            DatabaseQueryError: If query execution fails
        """
        try:
            logger.info(
                codes.DB_QUERY_STARTED,
                operation="find_all",
                model=self.model_class.__name__,
            )

            query = session.query(self.model_class)

            if not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            if order_by:
                order_column = getattr(self.model_class, order_by)
                if order_desc:
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column)

            if offset is not None:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            results = query.all()

            logger.info(
                codes.DB_QUERY_COMPLETED, operation="find_all", count=len(results)
            )

            return results

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED, operation="find_all", error=str(e), exc_info=True
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="find_all",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def find_by_field(
        self,
        session: Session,
        field_name: str,
        field_value: Any,
        include_deleted: bool = False,
    ) -> Optional[ModelType]:
        """
        Find entity by any field value.

        Uses parameterized query to prevent SQL injection.

        Args:
            session: Database session
            field_name: Name of the field to search
            field_value: Value to search for (parameterized)
            include_deleted: If True, include soft-deleted records

        Returns:
            Entity if found, None otherwise

        Raises:
            DatabaseQueryError: If query execution fails
        """
        try:
            logger.info(
                codes.DB_QUERY_STARTED,
                operation="find_by_field",
                model=self.model_class.__name__,
                field=field_name,
            )

            # Get column from model class
            if not hasattr(self.model_class, field_name):
                raise ValueError(
                    f"Field {field_name} does not exist on {self.model_class.__name__}"
                )

            field_column = getattr(self.model_class, field_name)

            query = session.query(self.model_class).filter(
                field_column == field_value  # Parameterized
            )

            if not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            result = query.first()

            logger.info(
                codes.DB_QUERY_COMPLETED,
                operation="find_by_field",
                found=result is not None,
            )

            return result

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="find_by_field",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query=f"find_by_field({field_name})",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def find_by_fields(
        self, session: Session, filters: Dict[str, Any], include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Find entities matching multiple field conditions.

        Uses parameterized queries for all conditions.

        Args:
            session: Database session
            filters: Dictionary of {field_name: value} to filter by
            include_deleted: If True, include soft-deleted records

        Returns:
            List of matching entities

        Raises:
            DatabaseQueryError: If query execution fails
        """
        try:
            logger.info(
                codes.DB_QUERY_STARTED,
                operation="find_by_fields",
                model=self.model_class.__name__,
                filters=filters,
            )

            query = session.query(self.model_class)

            # Add all filter conditions (parameterized)
            conditions = []
            for field_name, field_value in filters.items():
                if not hasattr(self.model_class, field_name):
                    raise ValueError(
                        f"Field {field_name} does not exist on {self.model_class.__name__}"
                    )

                field_column = getattr(self.model_class, field_name)
                conditions.append(field_column == field_value)

            if conditions:
                query = query.filter(and_(*conditions))

            if not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            results = query.all()

            logger.info(
                codes.DB_QUERY_COMPLETED, operation="find_by_fields", count=len(results)
            )

            return results

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="find_by_fields",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query=f"find_by_fields({filters})",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def create(self, session: Session, entity: ModelType) -> ModelType:
        """
        Create new entity in database.

        Args:
            session: Database session
            entity: Entity instance to create

        Returns:
            Created entity with populated fields

        Raises:
            DatabaseQueryError: If creation fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="create",
                model=self.model_class.__name__,
            )

            session.add(entity)
            session.flush()  # Get ID and trigger constraints without committing

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="create",
                entity_id=entity.id,
                msg=constants.MSG_DB_ENTITY_CREATED,
            )

            return entity

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="create",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_CREATION_FAILED,
                query="create",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def update(self, session: Session, entity: ModelType) -> ModelType:
        """
        Update existing entity.

        Automatically updates the updated_at timestamp.

        Args:
            session: Database session
            entity: Entity instance with updated fields

        Returns:
            Updated entity

        Raises:
            DatabaseQueryError: If update fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="update",
                model=self.model_class.__name__,
                entity_id=entity.id,
            )

            entity.update_timestamp()
            session.merge(entity)
            session.flush()

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="update",
                entity_id=entity.id,
                msg=constants.MSG_DB_ENTITY_UPDATED,
            )

            return entity

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="update",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="update",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def delete(self, session: Session, entity_id: str) -> bool:
        """
        Soft delete entity by ID.

        Sets deleted_at timestamp but keeps record in database.

        Args:
            session: Database session
            entity_id: ID of entity to delete

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseQueryError: If deletion fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="soft_delete",
                model=self.model_class.__name__,
                entity_id=entity_id,
            )

            entity = self.find_by_id(session, entity_id, include_deleted=False)
            if entity is None:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity_id=entity_id,
                    msg=constants.MSG_DB_ENTITY_NOT_FOUND,
                )
                return False

            entity.soft_delete()
            session.merge(entity)
            session.flush()

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="soft_delete",
                entity_id=entity_id,
                msg=constants.MSG_DB_ENTITY_DELETED,
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="soft_delete",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_DELETION_FAILED,
                query="delete",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def hard_delete(self, session: Session, entity_id: str) -> bool:
        """
        Permanently delete entity from database.

        WARNING: This permanently removes the record. Use with caution.

        Args:
            session: Database session
            entity_id: ID of entity to delete permanently

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseQueryError: If deletion fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="hard_delete",
                model=self.model_class.__name__,
                entity_id=entity_id,
            )

            entity = self.find_by_id(session, entity_id, include_deleted=True)
            if entity is None:
                logger.warning(
                    codes.DB_ENTITY_NOT_FOUND,
                    entity_id=entity_id,
                    msg=constants.MSG_DB_ENTITY_NOT_FOUND,
                )
                return False

            session.delete(entity)
            session.flush()

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="hard_delete",
                entity_id=entity_id,
                msg=constants.MSG_DB_ENTITY_DELETED,
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="hard_delete",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_DELETION_FAILED,
                query="hard_delete",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def count(self, session: Session, include_deleted: bool = False) -> int:
        """
        Count total number of entities.

        Args:
            session: Database session
            include_deleted: If True, include soft-deleted records

        Returns:
            Count of entities

        Raises:
            DatabaseQueryError: If count fails
        """
        try:
            query = session.query(func.count(self.model_class.id))

            if not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            count = query.scalar()
            return count or 0

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED, operation="count", error=str(e), exc_info=True
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="count",
                details={"model": self.model_class.__name__},
                original_error=e,
            ) from e

    def exists(self, session: Session, entity_id: str) -> bool:
        """
        Check if entity exists by ID.

        Args:
            session: Database session
            entity_id: ID to check

        Returns:
            True if exists, False otherwise
        """
        return self.find_by_id(session, entity_id) is not None
