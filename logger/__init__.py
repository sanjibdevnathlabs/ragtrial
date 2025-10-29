"""
Logging package for structured JSON logging using structlog.

Provides production-ready logging with JSON output, ISO 8601 timestamps,
and security sanitization for sensitive data.

Usage:
    from logger import setup_logging, get_logger, sanitize_log_data

    setup_logging(logging_config, app_config)
    logger = get_logger(__name__)

    # Sanitize sensitive data before logging
    safe_data = sanitize_log_data({"api_key": "secret", "user": "john"})
    logger.info("user_created", **safe_data)
"""

from logger.security import mask_api_key, sanitize_log_data
from logger.setup import get_logger, setup_logging

__all__ = ["setup_logging", "get_logger", "sanitize_log_data", "mask_api_key"]
