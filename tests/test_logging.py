"""
Tests for logging system.

Tests the logger package setup and configuration.
"""

from config import Config
from logger import get_logger, setup_logging


def test_logging_setup():
    """Test that logging can be initialized without errors"""
    app_config = Config()

    # Should not raise any exceptions
    setup_logging(app_config.logging, app_config.app)


def test_get_logger():
    """Test that get_logger returns a logger instance"""
    app_config = Config()
    setup_logging(app_config.logging, app_config.app)

    logger = get_logger(__name__)

    # Verify logger is returned
    assert logger is not None


def test_logger_basic_logging():
    """Test basic logging operations"""
    app_config = Config()
    setup_logging(app_config.logging, app_config.app)
    logger = get_logger(__name__)

    # These should not raise exceptions
    logger.debug("debug_message", detail="Debug")
    logger.info("info_message", detail="Info")
    logger.warning("warning_message", detail="Warning")
    logger.error("error_message", detail="Error")


def test_logger_structured_data():
    """Test logging with structured data"""
    app_config = Config()
    setup_logging(app_config.logging, app_config.app)
    logger = get_logger(__name__)

    # Should handle structured data without errors
    logger.info(
        "user_action", user_id="user_123", action="login", ip_address="192.168.1.1"
    )


def test_logger_exception_handling():
    """Test logging with exceptions"""
    app_config = Config()
    setup_logging(app_config.logging, app_config.app)
    logger = get_logger(__name__)

    # Should handle exception logging
    try:
        _ = 1 / 0
    except ZeroDivisionError:
        logger.error(
            "division_error", message="Attempted division by zero", exc_info=True
        )


def test_logging_respects_config():
    """Test that logging respects configuration settings"""
    app_config = Config()

    # Verify config is loaded
    assert app_config.logging.level is not None
    assert app_config.logging.format is not None

    # Setup with config
    setup_logging(app_config.logging, app_config.app)

    # Should complete without errors
    logger = get_logger(__name__)
    logger.info("test_message")
