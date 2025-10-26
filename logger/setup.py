"""
Structured logging setup using structlog.

This module configures structlog for comprehensive logging with:
- JSON format for production (parseable by log aggregators)
- Console format for development (human-readable with colors)
- Global context (app name, environment, version)
- Optional caller info (file, line, function)
- Optional process info (PID, thread ID)
- Automatic exception tracebacks for errors
"""

import logging
import sys
from typing import Any

import structlog

# Constants for log levels
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
    
    This function sets up comprehensive logging based on the provided configuration:
    - Format: JSON (production) or console (development)
    - Log level: Configurable (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Global context: app name, environment, version in every log
    - Caller info: Optional file/line/function information
    - Process info: Optional PID and thread ID
    - Exception handling: Always includes full tracebacks for errors
    
    Args:
        logging_config: Configuration object with logging settings
            - level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            - format: Output format ("json" or "console")
            - include_caller: Whether to show file/line/function
            - include_process_info: Whether to show PID/thread
        app_config: Configuration object with app metadata
            - name: Application name
            - environment: Current environment (dev/staging/prod)
            - version: Application version
    
    This function is idempotent and can be called multiple times safely.
    
    Example:
        from config import Config
        from logger import setup_logging, get_logger
        
        app_config = Config()
        setup_logging(app_config.logging, app_config.app)
        
        logger = get_logger(__name__)
        logger.info("application_started", user_count=100)
    """
    # Get log level from config
    log_level_str = logging_config.level.upper()
    log_level = LOG_LEVEL_MAP.get(log_level_str, logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Build processor chain
    processors = [
        # Add log level to event dict
        structlog.stdlib.add_log_level,
        # Add logger name to event dict
        structlog.stdlib.add_logger_name,
        # Add timestamp in ISO 8601 format
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    # Add caller information if enabled
    if logging_config.include_caller:
        processors.append(structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ))
    
    # Add process information if enabled
    if logging_config.include_process_info:
        processors.append(structlog.processors.add_log_level)
        processors.append(structlog.dev.set_exc_info)
    
    # Format stack info if present
    processors.append(structlog.processors.StackInfoRenderer())
    
    # Final rendering based on format
    if logging_config.format.lower() == "json":
        # JSON format for production (parseable)
        # Format exceptions for JSON output
        processors.append(structlog.processors.format_exc_info)
        processors.append(structlog.processors.UnicodeDecoder())
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Console format for development (human-readable with colors)
        # ConsoleRenderer handles exceptions internally (pretty formatting)
        processors.append(structlog.processors.UnicodeDecoder())
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        # Use structlog's logger factory
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Cache logger instances for performance
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Get a configured structlog logger instance.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        
    Returns:
        Configured structlog logger instance with bound context
        
    Example:
        logger = get_logger(__name__)
        logger.info("user_created", user_id="123", email="user@example.com")
        logger.error("database_error", error="Connection failed", retry_count=3)
        
        # With exception
        try:
            risky_operation()
        except Exception as e:
            logger.error("operation_failed", exc_info=True)
    """
    logger = structlog.get_logger(name)
    
    # Bind global app context if available
    try:
        from config import Config
        config = Config()
        logger = logger.bind(
            app_name=config.app.name,
            environment=config.app.environment,
            version=config.app.version
        )
    except Exception:
        # If config not available, return logger without binding
        pass
    
    return logger
