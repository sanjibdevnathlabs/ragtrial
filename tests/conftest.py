"""
Pytest configuration and shared fixtures.

This file is automatically discovered by pytest and provides
shared fixtures and configuration for all tests.

Key Features:
- Sets APP_ENV=test for all tests
- Adds project root to Python path
- Provides shared fixtures
"""

import os
import sys
from pathlib import Path

import pytest

# ============================================================================
# TEST ENVIRONMENT SETUP (runs before any imports)
# ============================================================================
from api.utils.singleton import SingletonMeta

# Set test environment - this ensures test.toml is loaded
os.environ["APP_ENV"] = "test"

# Add project root to Python path so tests can import application modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset singleton instances before each test.
    
    This ensures test isolation when using singleton pattern.
    Each test gets fresh service instances with their own mocks.
    """
    # Clear singleton instances before test
    SingletonMeta._instances.clear()
    yield
    # Optional: Clear after test as well for cleanliness
    SingletonMeta._instances.clear()


@pytest.fixture
def project_root_path():
    """Fixture providing the project root path"""
    return Path(__file__).parent.parent

