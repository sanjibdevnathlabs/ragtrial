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
    """Test that [app] section loads correctly (using test.toml or ci.toml)"""
    app_config = Config()

    # Test app config fields (from test.toml or ci.toml in CI)
    assert app_config.app.name in ["ragtrial-app-test", "ragtrial-app-ci"]
    assert app_config.app.version == "1.0.0"
    assert app_config.app.environment in ["test", "ci"]


def test_logging_config_section():
    """Test that [logging] section loads correctly (using test.toml)"""
    app_config = Config()

    # Test logging config fields (from test.toml)
    assert app_config.logging.level == "WARNING"  # Reduced noise during tests
    assert app_config.logging.format == "json"


def test_google_config_section():
    """Test that [google] section loads correctly"""
    app_config = Config()

    # Test google config exists (api_key may be None if env var not set)
    assert hasattr(app_config, "google")
    assert hasattr(app_config.google, "api_key")


def test_config_consistency():
    """Test that Config produces consistent values across instantiations (using test.toml or ci.toml)"""
    config1 = Config()
    config2 = Config()

    # Both should have same values (loaded from test.toml or ci.toml in CI)
    assert config1.app.name == config2.app.name
    assert config1.app.name in ["ragtrial-app-test", "ragtrial-app-ci"]
    assert config1.logging.level == config2.logging.level


def test_populate_config_section_helper():
    """Test that the _populate_config_section helper works correctly"""
    app_config = Config()

    # Verify all sections were populated using the helper
    # If any field is missing, the helper didn't work
    assert app_config.app.name is not None
    assert app_config.logging.level is not None
    assert app_config.logging.format is not None
