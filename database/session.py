"""
Database session factory with master-slave support.

This module provides a singleton SessionFactory for creating database sessions
with read/write splitting and query logging integration.
"""

import trace.codes as codes
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

import constants
from config import Config
from database.connection import ConnectionStringBuilder
from database.exceptions import DatabaseSessionError
from database.query_logger import QueryLogger
from logger import get_logger
from utils.singleton import SingletonMeta

logger = get_logger(__name__)


class SessionFactory(metaclass=SingletonMeta):
    """
    Singleton session factory for database operations.

    Provides read/write session splitting for master-slave architecture
    with automatic query logging when debug mode is enabled.
    """

    def __init__(self):
        """
        Initialize session factory.

        Due to singleton pattern, this only runs once per process.
        """
        if hasattr(self, "_initialized"):
            return

        logger.info(codes.DB_INITIALIZING)

        self._config: Optional[Config] = None
        self._write_engine: Optional[Engine] = None
        self._read_engine: Optional[Engine] = None
        self._WriteSession: Optional[sessionmaker] = None
        self._ReadSession: Optional[sessionmaker] = None

        self._initialized = True

        logger.info(codes.DB_INITIALIZED, msg=constants.MSG_DB_INITIALIZED)

    def _ensure_config_initialized(self) -> None:
        """Ensure config is initialized (lazy initialization)."""
        if self._config is None:
            self._config = Config()

    def _ensure_engines_initialized(self) -> None:
        """
        Ensure database engines are initialized (lazy initialization).

        Creates write and read engines with proper pooling and logging.
        """
        if self._write_engine is not None and self._read_engine is not None:
            return

        self._ensure_config_initialized()

        connection_builder = ConnectionStringBuilder(self._config)

        # Create WRITE engine
        logger.info(codes.DB_ENGINE_CREATING, mode=constants.DB_MODE_WRITE)

        write_url = connection_builder.build(constants.DB_MODE_WRITE)
        write_pool_config = connection_builder.get_pool_config(constants.DB_MODE_WRITE)

        # Build engine kwargs with only provided pool settings
        engine_kwargs = {
            "pool_pre_ping": write_pool_config["pool_pre_ping"],
            "pool_recycle": write_pool_config["pool_recycle"],
            "echo": False,  # We use custom query logger
        }

        # Only add pool_size and max_overflow if provided (not for SQLite)
        if "pool_size" in write_pool_config:
            engine_kwargs["pool_size"] = write_pool_config["pool_size"]
        if "max_overflow" in write_pool_config:
            engine_kwargs["max_overflow"] = write_pool_config["max_overflow"]

        self._write_engine = create_engine(write_url, **engine_kwargs)

        # Attach query logger if debug enabled
        if connection_builder.is_debug_enabled(constants.DB_MODE_WRITE):
            query_logger = QueryLogger(constants.DB_MODE_WRITE)
            query_logger.attach_to_engine(self._write_engine)

        logger.info(
            codes.DB_ENGINE_CREATED,
            mode=constants.DB_MODE_WRITE,
            msg=constants.MSG_DB_ENGINE_CREATED,
        )

        # Create READ engine
        logger.info(codes.DB_ENGINE_CREATING, mode=constants.DB_MODE_READ)

        read_url = connection_builder.build(constants.DB_MODE_READ)
        read_pool_config = connection_builder.get_pool_config(constants.DB_MODE_READ)

        # Build engine kwargs with only provided pool settings
        engine_kwargs = {
            "pool_pre_ping": read_pool_config["pool_pre_ping"],
            "pool_recycle": read_pool_config["pool_recycle"],
            "echo": False,
        }

        # Only add pool_size and max_overflow if provided (not for SQLite)
        if "pool_size" in read_pool_config:
            engine_kwargs["pool_size"] = read_pool_config["pool_size"]
        if "max_overflow" in read_pool_config:
            engine_kwargs["max_overflow"] = read_pool_config["max_overflow"]

        self._read_engine = create_engine(read_url, **engine_kwargs)

        # Attach query logger if debug enabled
        if connection_builder.is_debug_enabled(constants.DB_MODE_READ):
            query_logger = QueryLogger(constants.DB_MODE_READ)
            query_logger.attach_to_engine(self._read_engine)

        logger.info(
            codes.DB_ENGINE_CREATED,
            mode=constants.DB_MODE_READ,
            msg=constants.MSG_DB_ENGINE_CREATED,
        )

        # Create session makers
        self._WriteSession = sessionmaker(bind=self._write_engine)
        self._ReadSession = sessionmaker(bind=self._read_engine)

    @contextmanager
    def get_write_session(self) -> Generator[Session, None, None]:
        """
        Get database session for WRITE operations (master).

        Context manager that automatically commits on success and rolls back on error.

        Usage:
            with session_factory.get_write_session() as session:
                user = User(name="John")
                session.add(user)
                # Auto-commits on exit, rolls back on exception

        Yields:
            SQLAlchemy session for write operations

        Raises:
            DatabaseSessionError: If session creation fails
        """
        self._ensure_engines_initialized()

        logger.info(codes.DB_SESSION_CREATING, mode=constants.DB_MODE_WRITE)

        session = None
        try:
            session = self._WriteSession()
            logger.info(
                codes.DB_SESSION_CREATED,
                mode=constants.DB_MODE_WRITE,
                msg=constants.MSG_DB_SESSION_CREATED,
            )

            yield session

            logger.info(codes.DB_TRANSACTION_COMMITTED)
            session.commit()

        except Exception as e:
            if session:
                logger.error(codes.DB_TRANSACTION_FAILED, error=str(e), exc_info=True)
                session.rollback()
                logger.info(
                    codes.DB_TRANSACTION_ROLLED_BACK,
                    msg=constants.MSG_DB_TRANSACTION_ROLLED_BACK,
                )

            raise DatabaseSessionError(
                message=constants.ERROR_DB_SESSION_CREATION_FAILED,
                details={"mode": constants.DB_MODE_WRITE},
                original_error=e,
            ) from e

        finally:
            if session:
                session.close()
                logger.info(
                    codes.DB_SESSION_CLOSED,
                    mode=constants.DB_MODE_WRITE,
                    msg=constants.MSG_DB_SESSION_CLOSED,
                )

    @contextmanager
    def get_read_session(self) -> Generator[Session, None, None]:
        """
        Get database session for READ operations (slave/replica).

        Context manager for read-only queries. Uses read replica if configured.

        Usage:
            with session_factory.get_read_session() as session:
                users = session.query(User).all()

        Yields:
            SQLAlchemy session for read operations

        Raises:
            DatabaseSessionError: If session creation fails
        """
        self._ensure_engines_initialized()

        logger.info(codes.DB_SESSION_CREATING, mode=constants.DB_MODE_READ)

        session = None
        try:
            session = self._ReadSession()
            logger.info(
                codes.DB_SESSION_CREATED,
                mode=constants.DB_MODE_READ,
                msg=constants.MSG_DB_SESSION_CREATED,
            )

            yield session

        except Exception as e:
            logger.error(
                codes.DB_SESSION_ERROR,
                error=str(e),
                mode=constants.DB_MODE_READ,
                exc_info=True,
            )

            raise DatabaseSessionError(
                message=constants.ERROR_DB_SESSION_CREATION_FAILED,
                details={"mode": constants.DB_MODE_READ},
                original_error=e,
            ) from e

        finally:
            if session:
                session.close()
                logger.info(
                    codes.DB_SESSION_CLOSED,
                    mode=constants.DB_MODE_READ,
                    msg=constants.MSG_DB_SESSION_CLOSED,
                )

    def get_write_engine(self) -> Engine:
        """
        Get write engine directly (for migrations and admin operations).

        Returns:
            SQLAlchemy engine for write operations
        """
        self._ensure_engines_initialized()
        return self._write_engine

    def dispose_all(self) -> None:
        """
        Dispose all database connections.

        Should be called on application shutdown.
        """
        if self._write_engine:
            self._write_engine.dispose()
            logger.info(codes.DB_ENGINE_DISPOSED, mode=constants.DB_MODE_WRITE)

        if self._read_engine:
            self._read_engine.dispose()
            logger.info(codes.DB_ENGINE_DISPOSED, mode=constants.DB_MODE_READ)
