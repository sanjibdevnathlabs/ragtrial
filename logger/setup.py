"""
Structured logging setup using structlog.

Configures structlog for production-ready logging with JSON/console output,
global context, and optional caller/process information.
"""

import logging
import sys
from typing import Any, List

import structlog

LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logging(logging_config: Any, app_config: Any) -> None:
    """
    Configure structured logging with structlog.

    Args:
        logging_config: Logging settings (level, format, caller, process info)
        app_config: App metadata (name, environment, version)
    """
    log_level = LOG_LEVEL_MAP.get(logging_config.level.upper(), logging.INFO)

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)

    processors = _build_processors(logging_config)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _build_processors(logging_config: Any) -> List:
    """Build processor chain based on configuration."""
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if logging_config.include_caller:
        processors.append(
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            )
        )

    if logging_config.include_process_info:
        processors.append(structlog.processors.add_log_level)
        processors.append(structlog.dev.set_exc_info)

    processors.append(structlog.processors.StackInfoRenderer())

    if logging_config.format.lower() == "json":
        processors.append(structlog.processors.format_exc_info)
        processors.append(structlog.processors.UnicodeDecoder())
        processors.append(structlog.processors.JSONRenderer())
        return processors

    processors.append(structlog.processors.UnicodeDecoder())
    processors.append(structlog.dev.ConsoleRenderer(colors=True))
    return processors


def get_logger(name: str) -> Any:
    """
    Get a configured structlog logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        Configured structlog logger instance with optional app context binding
    """
    logger = structlog.get_logger(name)

    try:
        from config import Config

        config = Config()
        return logger.bind(
            app_name=config.app.name,
            environment=config.app.environment,
            version=config.app.version,
        )
    except Exception:
        return logger
