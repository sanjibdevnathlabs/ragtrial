"""
Pytest configuration and shared fixtures.

This file is automatically discovered by pytest and provides
shared fixtures and configuration for all tests.

Key Features:
- Sets APP_ENV=test for all tests
- Adds project root to Python path
- Provides mock fixtures for external dependencies
- Ensures test isolation with singleton reset
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

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


# ============================================================================
# SINGLETON RESET - Critical for Test Isolation
# ============================================================================


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


# ============================================================================
# MOCK FIXTURES - Database, Vector Store, Embeddings
# ============================================================================


@pytest.fixture
def mock_db_engine():
    """
    Mock SQLAlchemy engine for database operations.

    Use this fixture to avoid real database connections.
    Returns MagicMock that supports context manager protocol.
    """
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    mock_engine.connect.return_value.__exit__.return_value = None
    return mock_engine


@pytest.fixture
def mock_db_session():
    """
    Mock SQLAlchemy session for database operations.

    Use this fixture to avoid real database connections.
    Returns MagicMock with common session methods.
    """
    mock_session = MagicMock()
    mock_session.execute.return_value = MagicMock()
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    return mock_session


@pytest.fixture
def mock_vectorstore():
    """
    Mock vector store client (ChromaDB, Qdrant, etc.).

    Use this fixture to avoid real vector store connections.
    Returns MagicMock with common vector store methods.
    """
    mock_store = MagicMock()
    mock_store.add_documents.return_value = None
    mock_store.search.return_value = []
    mock_store.clear.return_value = None
    return mock_store


@pytest.fixture
def mock_embeddings():
    """
    Mock embeddings provider (Google AI, OpenAI, etc.).

    Use this fixture to avoid real API calls.
    Returns MagicMock with fake embedding vectors.
    """
    mock_embed = MagicMock()
    # Fake 384-dimensional embedding vector
    fake_embedding = [0.1] * 384
    mock_embed.embed_query.return_value = fake_embedding
    mock_embed.embed_documents.return_value = [fake_embedding]
    return mock_embed


@pytest.fixture
def mock_llm():
    """
    Mock LLM provider (Google Gemini, OpenAI, etc.).

    Use this fixture to avoid real LLM API calls.
    Returns MagicMock with fake responses.
    """
    mock = MagicMock()
    mock.invoke.return_value = "This is a mock LLM response."
    mock.generate.return_value = "This is a mock generated text."
    return mock


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def project_root_path():
    """Fixture providing the project root path"""
    return Path(__file__).parent.parent


# ============================================================================
# TEST CLEANUP - Remove test artifacts after test session
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_artifacts():
    """
    Clean up test artifacts after all tests complete.

    This fixture runs once at the end of the entire test session
    and removes test-related storage directories.

    Note: Database cleanup is handled per-test in integration test fixtures.
    MySQL database tables are truncated, not deleted.

    Cleaned up:
    - storage/chroma_test/ (ChromaDB test collection)
    - storage/test_documents/ (Test document storage)
    """
    # Yield to run tests first
    yield

    # Cleanup after all tests complete
    import shutil
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    storage_dir = project_root / "storage"

    cleanup_paths = [
        storage_dir / "chroma_test",
        storage_dir / "test_documents",
    ]

    for path in cleanup_paths:
        try:
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
                print(f"✓ Cleaned up: {path}")
        except Exception as e:
            print(f"⚠ Failed to clean up {path}: {e}")
