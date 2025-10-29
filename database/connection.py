"""
Database connection string builder.

This module provides a builder class for generating database connection
strings for SQLite, MySQL, and PostgreSQL with read/write mode support.

Supported Databases:
    - SQLite (file-based or in-memory)
    - MySQL (with PyMySQL driver)
    - PostgreSQL (with psycopg2 driver)

Connection Modes:
    - READ: For read-only queries (slave/replica)
    - WRITE: For write operations (master)
"""

import trace.codes as codes
from typing import Union
from urllib.parse import quote_plus

import constants
from config import (
    Config,
    MySQLReadConfig,
    MySQLWriteConfig,
    PostgreSQLReadConfig,
    PostgreSQLWriteConfig,
    SQLiteReadConfig,
    SQLiteWriteConfig,
)
from database.exceptions import DatabaseConnectionError
from logger import get_logger

logger = get_logger(__name__)


class ConnectionStringBuilder:
    """
    Build database connection strings for different drivers and modes.

    Supports SQLite, MySQL, and PostgreSQL with read/write mode separation
    for master-slave architecture.
    """

    def __init__(self, config: Config):
        """
        Initialize connection string builder.

        Args:
            config: Application configuration with database settings
        """
        self.config = config
        self.driver = config.database.driver.lower()

    def build(self, mode: str = constants.DB_MODE_WRITE) -> str:
        """
        Build connection string for specified mode.

        Args:
            mode: Connection mode (READ or WRITE)

        Returns:
            Database connection string

        Raises:
            DatabaseConnectionError: If driver is unsupported
        """
        if self.driver == constants.DB_DRIVER_SQLITE:
            return self._build_sqlite(mode)

        if self.driver == constants.DB_DRIVER_MYSQL:
            return self._build_mysql(mode)

        if self.driver == constants.DB_DRIVER_POSTGRESQL:
            return self._build_postgresql(mode)

        logger.error(
            codes.DB_CONNECTION_FAILED,
            driver=self.driver,
            error=constants.ERROR_DB_DRIVER_UNSUPPORTED,
        )
        raise DatabaseConnectionError(
            message=constants.ERROR_DB_DRIVER_UNSUPPORTED,
            details={"driver": self.driver},
        )

    def _build_sqlite(self, mode: str) -> str:
        """
        Build SQLite connection string.

        Args:
            mode: Connection mode (READ or WRITE)

        Returns:
            SQLite connection string (e.g., "sqlite:///storage/metadata.db")
        """
        cfg: Union[SQLiteWriteConfig, SQLiteReadConfig]

        if mode == constants.DB_MODE_READ:
            cfg = self.config.database.sqlite.read
        else:
            cfg = self.config.database.sqlite.write

        return f"{constants.DB_PREFIX_SQLITE}{cfg.path}"

    def _build_mysql(self, mode: str) -> str:
        """
        Build MySQL connection string with PyMySQL driver.

        Args:
            mode: Connection mode (READ or WRITE)

        Returns:
            MySQL connection string
            (e.g., "mysql+pymysql://user:pass@host:3306/dbname?charset=utf8mb4")
        """
        cfg: Union[MySQLWriteConfig, MySQLReadConfig]

        if mode == constants.DB_MODE_READ:
            cfg = self.config.database.mysql.read
        else:
            cfg = self.config.database.mysql.write

        # URL-encode username and password to handle special characters
        username = quote_plus(cfg.username)
        password = quote_plus(cfg.password) if cfg.password else ""

        # Build connection string
        connection_string = f"{constants.DB_PREFIX_MYSQL}{username}"

        if password:
            connection_string += f":{password}"

        connection_string += f"@{cfg.host}:{cfg.port}/{cfg.database}"

        # Add charset parameter
        if cfg.charset:
            connection_string += f"?charset={cfg.charset}"

        return connection_string

    def _build_postgresql(self, mode: str) -> str:
        """
        Build PostgreSQL connection string with psycopg2 driver.

        Args:
            mode: Connection mode (READ or WRITE)

        Returns:
            PostgreSQL connection string
            (e.g., "postgresql+psycopg2://user:pass@host:5432/dbname")
        """
        cfg: Union[PostgreSQLWriteConfig, PostgreSQLReadConfig]

        if mode == constants.DB_MODE_READ:
            cfg = self.config.database.postgresql.read
        else:
            cfg = self.config.database.postgresql.write

        # URL-encode username and password to handle special characters
        username = quote_plus(cfg.username)
        password = quote_plus(cfg.password) if cfg.password else ""

        # Build connection string
        connection_string = f"{constants.DB_PREFIX_POSTGRESQL}{username}"

        if password:
            connection_string += f":{password}"

        connection_string += f"@{cfg.host}:{cfg.port}/{cfg.database}"

        return connection_string

    def get_pool_config(self, mode: str = constants.DB_MODE_WRITE) -> dict:
        """
        Get connection pool configuration for specified mode.

        Args:
            mode: Connection mode (READ or WRITE)

        Returns:
            Dictionary with pool configuration:
                - pool_size: Number of connections to keep open
                - max_overflow: Maximum overflow connections
                - pool_pre_ping: Test connections before use
                - pool_recycle: Recycle connections after N seconds
        """
        if self.driver == constants.DB_DRIVER_SQLITE:
            # SQLite doesn't need connection pooling (single file)
            # Note: Don't include max_overflow for SQLite - it uses SingletonThreadPool
            return {
                "pool_pre_ping": False,
                "pool_recycle": -1,
            }

        # Get database-specific config
        if self.driver == constants.DB_DRIVER_MYSQL:
            if mode == constants.DB_MODE_READ:
                cfg = self.config.database.mysql.read
            else:
                cfg = self.config.database.mysql.write
        elif self.driver == constants.DB_DRIVER_POSTGRESQL:
            if mode == constants.DB_MODE_READ:
                cfg = self.config.database.postgresql.read
            else:
                cfg = self.config.database.postgresql.write
        else:
            # Fallback to defaults
            return {
                "pool_size": constants.DB_POOL_SIZE_DEFAULT,
                "max_overflow": constants.DB_MAX_OVERFLOW_DEFAULT,
                "pool_pre_ping": constants.DB_POOL_PRE_PING_DEFAULT,
                "pool_recycle": constants.DB_POOL_RECYCLE_DEFAULT,
            }

        return {
            "pool_size": cfg.pool_size,
            "max_overflow": cfg.max_overflow,
            "pool_pre_ping": self.config.database.pool_pre_ping,
            "pool_recycle": self.config.database.pool_recycle,
        }

    def is_debug_enabled(self, mode: str = constants.DB_MODE_WRITE) -> bool:
        """
        Check if query debugging is enabled for specified mode.

        Args:
            mode: Connection mode (READ or WRITE)

        Returns:
            True if debug logging is enabled
        """
        if self.driver == constants.DB_DRIVER_SQLITE:
            if mode == constants.DB_MODE_READ:
                return self.config.database.sqlite.read.debug
            return self.config.database.sqlite.write.debug

        if self.driver == constants.DB_DRIVER_MYSQL:
            if mode == constants.DB_MODE_READ:
                return self.config.database.mysql.read.debug
            return self.config.database.mysql.write.debug

        if self.driver == constants.DB_DRIVER_POSTGRESQL:
            if mode == constants.DB_MODE_READ:
                return self.config.database.postgresql.read.debug
            return self.config.database.postgresql.write.debug

        return False
