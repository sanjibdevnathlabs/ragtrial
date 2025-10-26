"""
Tests for configuration system.

Tests the Config class and the refactored _populate_config_section helper.
"""

from config import Config


def test_config_loading():
    """Test that configuration loads correctly from TOML files"""
    # Load config
    app_config = Config()
    
    # Verify config object is created
    assert app_config is not None


def test_app_config_section():
    """Test that [app] section loads correctly"""
    app_config = Config()
    
    # Test app config fields
    assert app_config.app.name == "ragtrial-app"  # Fixed: actual name in TOML files
    assert app_config.app.version == "1.0.0"
    # environment may vary based on APP_ENV
    assert app_config.app.environment is not None


def test_logging_config_section():
    """Test that [logging] section loads correctly"""
    app_config = Config()
    
    # Test logging config fields
    assert app_config.logging.level == "INFO"
    assert app_config.logging.format == "console"
    assert app_config.logging.include_caller is False
    assert app_config.logging.include_process_info is False


def test_google_config_section():
    """Test that [google] section loads correctly"""
    app_config = Config()
    
    # Test google config exists (api_key may be None if env var not set)
    assert hasattr(app_config, "google")
    assert hasattr(app_config.google, "api_key")


def test_config_consistency():
    """Test that Config produces consistent values across instantiations"""
    config1 = Config()
    config2 = Config()
    
    # Both should have same values (loaded from same TOML)
    assert config1.app.name == config2.app.name
    assert config1.app.name == "ragtrial-app"
    assert config1.logging.level == config2.logging.level


def test_populate_config_section_helper():
    """Test that the _populate_config_section helper works correctly"""
    app_config = Config()
    
    # Verify all sections were populated using the helper
    # If any field is missing, the helper didn't work
    assert app_config.app.name is not None
    assert app_config.logging.level is not None
    assert app_config.logging.format is not None

