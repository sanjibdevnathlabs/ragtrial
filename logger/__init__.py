"""
Logging package for structured JSON logging using structlog.

This package provides a production-ready logging setup with:
- JSON output format for easy parsing by log aggregation tools
- ISO 8601 timestamps
- Automatic exception formatting
- Context preservation

Usage:
    from logger import setup_logging, get_logger
    
    # Initialize logging (call once at application startup)
    setup_logging()
    
    # Get logger instance
    logger = get_logger(__name__)
    logger.info("message", key="value")
"""

from logger.setup import get_logger, setup_logging

__all__ = ["setup_logging", "get_logger"]

