"""
Entity Config entity model.

Polymorphic configuration storage for various entities in the application.
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy import Column, String, Text

import constants
from database.base_model import BaseModel


class EntityConfig(BaseModel):
    """
    Polymorphic entity configuration storage.

    Provides flexible configuration storage for any entity in the system.
    Multiple rows can form complete preferences for an entity.

    Fields:
        id: UUID primary key
        module_name: Module the entity belongs to (e.g., 'user', 'file')
        entity_type: Type of entity (e.g., 'preferences', 'settings')
        entity_id: UUID of the entity (e.g., user_id, file_id)
        config_key: Specific configuration key (e.g., 'upload_mode', 'theme')
        config_value: Value of the configuration (TEXT for JSON/metadata)
        created_at: Creation timestamp (inherited)
        updated_at: Update timestamp (inherited)
        deleted_at: Soft delete timestamp (inherited)

    Indexes:
        - idx_config_composite: Composite index (module_name(100), entity_type(100),
                                entity_id, config_key(100)) for fast lookups
        - idx_config_entity_id: For direct lookups by entity_id
        - idx_config_deleted_at: For filtering active vs deleted records

    Example Usage:
        # User preferences
        config = EntityConfig(
            module_name='user',
            entity_type='preferences',
            entity_id='user_123',
            config_key='upload_mode',
            config_value='async'
        )

        # File settings
        config = EntityConfig(
            module_name='file',
            entity_type='settings',
            entity_id='file_456',
            config_key='auto_index',
            config_value='true'
        )
    """

    __tablename__ = constants.DB_TABLE_ENTITY_CONFIG

    # Override table name from base model
    __table_args__ = {"extend_existing": True}

    # Entity config-specific fields
    module_name = Column(String(255), nullable=False)
    entity_type = Column(String(255), nullable=False)
    entity_id = Column(String(36), nullable=False, index=True)
    config_key = Column(String(255), nullable=False)
    config_value = Column(Text, nullable=True)

    @staticmethod
    def generate_id() -> str:
        """
        Generate a new UUID for entity config ID.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    def set_value(self, value: Any) -> None:
        """
        Set configuration value.

        Automatically serializes dict/list to JSON, stores primitives as strings.

        Args:
            value: Configuration value (str, int, bool, dict, list)
        """
        if isinstance(value, (dict, list)):
            self.config_value = json.dumps(value)
        else:
            self.config_value = str(value)
        self.update_timestamp()

    def get_value(self) -> Any:
        """
        Get configuration value.

        Attempts to deserialize JSON, returns string if not JSON.

        Returns:
            Configuration value (str, dict, list, or None)
        """
        if self.config_value is None:
            return None

        # Try to parse as JSON
        try:
            return json.loads(self.config_value)
        except json.JSONDecodeError:
            # Return as string if not JSON
            return self.config_value

    def get_value_as_bool(self) -> bool:
        """
        Get configuration value as boolean.

        Returns:
            Boolean value ('true', '1', 'yes' → True, everything else → False)
        """
        if self.config_value is None:
            return False

        value_lower = self.config_value.lower()
        return value_lower in ("true", "1", "yes", "on")

    def get_value_as_int(self, default: int = 0) -> int:
        """
        Get configuration value as integer.

        Args:
            default: Default value if conversion fails

        Returns:
            Integer value, or default if conversion fails
        """
        if self.config_value is None:
            return default

        try:
            return int(self.config_value)
        except (ValueError, TypeError):
            return default

    def get_composite_key(self) -> str:
        """
        Get composite key for this configuration.

        Returns:
            String in format: module_name.entity_type.entity_id.config_key
        """
        return (
            f"{self.module_name}.{self.entity_type}."
            f"{self.entity_id}.{self.config_key}"
        )

    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """
        Convert to dictionary with additional computed fields.

        Args:
            exclude: Fields to exclude

        Returns:
            Dictionary representation
        """
        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["is_deleted"] = self.is_deleted()
        data["composite_key"] = self.get_composite_key()
        # Deserialize value for API response
        data["parsed_value"] = self.get_value()

        return data

    def __repr__(self) -> str:
        """String representation."""
        deleted = " (DELETED)" if self.is_deleted() else ""
        value_preview = (
            self.config_value[:30] + "..."
            if self.config_value and len(self.config_value) > 30
            else self.config_value
        )
        return (
            f"<EntityConfig(id={self.id!r}, "
            f"key={self.get_composite_key()!r}, "
            f"value={value_preview!r})"
            f"{deleted}>"
        )

