"""
SQLAlchemy query logger with read/write mode support.

This module provides query logging functionality with proper mode labeling
([WRITE_DB] or [READ_DB]) for debugging and monitoring.
"""

import time
import trace.codes as codes

from sqlalchemy import event
from sqlalchemy.engine import Engine

import constants
from logger import get_logger

logger = get_logger(__name__)


class QueryLogger:
    """
    SQLAlchemy event listener for query logging.

    Logs queries with execution time and mode prefix.
    """

    def __init__(self, mode: str = constants.DB_MODE_WRITE):
        """
        Initialize query logger.

        Args:
            mode: Connection mode (READ or WRITE)
        """
        self.mode = mode
        self.prefix = (
            constants.QUERY_LOG_PREFIX_WRITE
            if mode == constants.DB_MODE_WRITE
            else constants.QUERY_LOG_PREFIX_READ
        )

    def attach_to_engine(self, engine: Engine):
        """
        Attach query logger to SQLAlchemy engine.

        Args:
            engine: SQLAlchemy engine instance
        """

        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            """Record query start time."""
            conn.info.setdefault("query_start_time", []).append(time.time())

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            """Log query with execution time."""
            total_time = time.time() - conn.info["query_start_time"].pop(-1)

            logger.info(
                codes.DB_QUERY_EXECUTED,
                mode=self.mode,
                prefix=self.prefix,
                query=statement[:500],  # Truncate long queries
                parameters=str(parameters)[:200] if parameters else None,
                execution_time_ms=round(total_time * 1000, 2),
                msg=constants.MSG_QUERY_EXECUTED,
            )
