"""
Entity Config repository with custom query methods.

Handles polymorphic configuration storage for various entities.
"""

import trace.codes as codes
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

import constants
from app.modules.entity_config.entity import EntityConfig
from database.base_repository import BaseRepository
from database.exceptions import DatabaseQueryError
from logger import get_logger

logger = get_logger(__name__)


class EntityConfigRepository(BaseRepository[EntityConfig]):
    """
    Repository for entity configuration operations.

    Extends BaseRepository with config-specific queries:
    - find_by_entity()
    - get_config_value()
    - set_config_value()
    - get_all_config()
    - delete_config()
    - delete_entity_config()
    """

    def __init__(self):
        """Initialize entity config repository."""
        super().__init__(EntityConfig)

    def find_by_entity(
        self,
        session: Session,
        module_name: str,
        entity_type: str,
        entity_id: str,
        include_deleted: bool = False,
    ) -> List[EntityConfig]:
        """
        Find all configuration entries for an entity.

        Args:
            session: Database session
            module_name: Module name (e.g., 'user', 'file')
            entity_type: Entity type (e.g., 'preferences', 'settings')
            entity_id: Entity ID (e.g., user_id)
            include_deleted: Include soft-deleted configs

        Returns:
            List of configuration entries
        """
        return self.find_by_fields(
            session,
            filters={
                "module_name": module_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
            },
            include_deleted=include_deleted,
        )

    def get_config_value(
        self,
        session: Session,
        module_name: str,
        entity_type: str,
        entity_id: str,
        config_key: str,
    ) -> Optional[str]:
        """
        Get configuration value for an entity.

        Args:
            session: Database session
            module_name: Module name
            entity_type: Entity type
            entity_id: Entity ID
            config_key: Configuration key

        Returns:
            Configuration value if found, None otherwise
        """
        configs = self.find_by_fields(
            session,
            filters={
                "module_name": module_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "config_key": config_key,
            },
            include_deleted=False,
        )
        
        return configs[0].config_value if configs else None

    def set_config_value(
        self,
        session: Session,
        module_name: str,
        entity_type: str,
        entity_id: str,
        config_key: str,
        config_value: str,
    ) -> EntityConfig:
        """
        Set configuration value for an entity.

        Creates new config entry if not exists, updates if exists.

        Args:
            session: Database session
            module_name: Module name
            entity_type: Entity type
            entity_id: Entity ID
            config_key: Configuration key
            config_value: Configuration value

        Returns:
            EntityConfig entry (created or updated)

        Raises:
            DatabaseQueryError: If operation fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="set_config_value",
                module=module_name,
                type=entity_type,
                entity_id=entity_id,
                key=config_key,
            )

            # Try to find existing config
            existing_configs = self.find_by_fields(
                session,
                filters={
                    "module_name": module_name,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "config_key": config_key,
                },
                include_deleted=False,
            )

            if existing_configs:
                # Update existing
                config = existing_configs[0]
                config.config_value = config_value
                config.update_timestamp()
                self.update(session, config)
            else:
                # Create new
                config = EntityConfig(
                    id=EntityConfig.generate_id(),
                    module_name=module_name,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    config_key=config_key,
                    config_value=config_value,
                )
                config = self.create(session, config)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="set_config_value",
                module=module_name,
                type=entity_type,
                entity_id=entity_id,
                key=config_key,
            )

            return config

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="set_config_value",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_UPDATE_FAILED,
                query="set_config_value",
                details={
                    "module_name": module_name,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "config_key": config_key,
                },
                original_error=e,
            ) from e

    def get_all_config(
        self,
        session: Session,
        module_name: str,
        entity_type: str,
        entity_id: str,
    ) -> Dict[str, str]:
        """
        Get all configuration for an entity as a dictionary.

        Args:
            session: Database session
            module_name: Module name
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            Dictionary of config_key -> config_value
        """
        configs = self.find_by_entity(
            session, module_name, entity_type, entity_id, include_deleted=False
        )
        
        return {config.config_key: config.config_value for config in configs}

    def delete_config(
        self,
        session: Session,
        module_name: str,
        entity_type: str,
        entity_id: str,
        config_key: str,
    ) -> bool:
        """
        Delete a specific configuration entry.

        Args:
            session: Database session
            module_name: Module name
            entity_type: Entity type
            entity_id: Entity ID
            config_key: Configuration key

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseQueryError: If delete fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="delete_config",
                module=module_name,
                type=entity_type,
                entity_id=entity_id,
                key=config_key,
            )

            configs = self.find_by_fields(
                session,
                filters={
                    "module_name": module_name,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "config_key": config_key,
                },
                include_deleted=False,
            )

            if not configs:
                logger.warning(codes.DB_ENTITY_NOT_FOUND, config_key=config_key)
                return False

            config = configs[0]
            self.soft_delete(session, config.id)

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="delete_config",
                module=module_name,
                type=entity_type,
                entity_id=entity_id,
                key=config_key,
            )

            return True

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="delete_config",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_DELETE_FAILED,
                query="delete_config",
                details={
                    "module_name": module_name,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "config_key": config_key,
                },
                original_error=e,
            ) from e

    def delete_entity_config(
        self,
        session: Session,
        module_name: str,
        entity_type: str,
        entity_id: str,
    ) -> int:
        """
        Delete all configuration for an entity.

        Args:
            session: Database session
            module_name: Module name
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            Number of config entries deleted

        Raises:
            DatabaseQueryError: If delete fails
        """
        try:
            logger.info(
                codes.DB_REPOSITORY_STARTED,
                operation="delete_entity_config",
                module=module_name,
                type=entity_type,
                entity_id=entity_id,
            )

            configs = self.find_by_entity(
                session, module_name, entity_type, entity_id, include_deleted=False
            )

            count = 0
            for config in configs:
                self.soft_delete(session, config.id)
                count += 1

            logger.info(
                codes.DB_REPOSITORY_COMPLETED,
                operation="delete_entity_config",
                module=module_name,
                type=entity_type,
                entity_id=entity_id,
                count=count,
            )

            return count

        except Exception as e:
            logger.error(
                codes.DB_REPOSITORY_FAILED,
                operation="delete_entity_config",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_ENTITY_DELETE_FAILED,
                query="delete_entity_config",
                details={
                    "module_name": module_name,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                },
                original_error=e,
            ) from e

    def find_by_module(
        self, session: Session, module_name: str, include_deleted: bool = False
    ) -> List[EntityConfig]:
        """
        Find all configuration entries for a module.

        Args:
            session: Database session
            module_name: Module name
            include_deleted: Include soft-deleted configs

        Returns:
            List of configuration entries
        """
        return self.find_by_fields(
            session, filters={"module_name": module_name}, include_deleted=include_deleted
        )

    def count_by_entity_type(
        self, session: Session, module_name: str, entity_type: str
    ) -> int:
        """
        Count configuration entries by entity type.

        Args:
            session: Database session
            module_name: Module name
            entity_type: Entity type

        Returns:
            Count of config entries
        """
        try:
            query = session.query(EntityConfig).filter(
                EntityConfig.module_name == module_name,
                EntityConfig.entity_type == entity_type,
                EntityConfig.deleted_at.is_(None),
            )
            return query.count()

        except Exception as e:
            logger.error(
                codes.DB_QUERY_FAILED,
                operation="count_by_entity_type",
                error=str(e),
                exc_info=True,
            )
            raise DatabaseQueryError(
                message=constants.ERROR_DB_QUERY_FAILED,
                query="count_by_entity_type",
                details={"module_name": module_name, "entity_type": entity_type},
                original_error=e,
            ) from e

