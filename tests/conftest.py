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
from utils.singleton import SingletonMeta

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


@pytest.fixture(autouse=True)
def clean_database_after_test():
    """
    Clean database data after each test for isolation.
    
    This ensures tests don't affect each other.
    Only runs if database tables exist.
    """
    yield
    
    # Clean up after test
    try:
        from database.session import SessionFactory
        from sqlalchemy import text
        
        sf = SessionFactory()
        with sf.get_write_session() as session:
            # Delete all records from files table
            session.execute(text("DELETE FROM files"))
    except Exception:
        # Silently ignore if tables don't exist or other errors
        pass


@pytest.fixture
def project_root_path():
    """Fixture providing the project root path"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Set up test database before all tests.
    
    This fixture:
    - Removes existing test database
    - Runs migrations to create schema
    - Runs once per test session
    """
    import subprocess
    
    # Clean up old test database
    test_db_path = project_root / "storage" / "test.db"
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Run migrations to create schema
    subprocess.run(
        ["python", "-m", "migration", "up"],
        cwd=str(project_root),
        capture_output=True
    )
    
    yield
    
    # Optional: Clean up after all tests
    if test_db_path.exists():
        test_db_path.unlink()

