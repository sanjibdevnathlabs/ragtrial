"""
Tests for health check service.

Tests health status endpoint functionality.
NOTE: See test_health_service.py for comprehensive unit tests.
This file tests the old interface for backwards compatibility.
"""

from unittest.mock import Mock, patch

import pytest

import constants
from app.modules.health import HealthService
from app.modules.health.response import HealthResponse


@pytest.fixture
def health_test_config():
    """Mock configuration for health tests."""
    config = Mock()
    config.database = Mock()
    config.database.driver = "mysql"
    config.database.type = "mysql"
    config.vectorstore = Mock()
    config.vectorstore.provider = "chroma"
    config.rag = Mock()
    config.rag.provider = "google"
    config.embeddings = Mock()
    config.embeddings.provider = "google"
    return config


class TestHealthService:
    """Test suite for HealthService."""

    @patch("app.modules.health.service.SessionFactory")
    @patch("app.modules.health.service.create_embeddings")
    @patch("app.modules.health.service.create_vectorstore")
    def test_get_health_status_returns_response(
        self, mock_vs, mock_emb, mock_session, health_test_config
    ):
        """Test health status returns HealthResponse."""
        # Mock database health check
        mock_session_instance = Mock()
        mock_session_instance.check_health.return_value = True
        mock_session.return_value = mock_session_instance

        # Mock vectorstore health check
        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vs.return_value = mock_vs_instance
        mock_emb.return_value = Mock()

        service = HealthService(health_test_config)
        result = service.get_health_status()

        assert isinstance(result, HealthResponse)

    @patch("app.modules.health.service.SessionFactory")
    @patch("app.modules.health.service.create_embeddings")
    @patch("app.modules.health.service.create_vectorstore")
    def test_get_health_status_has_correct_status(
        self, mock_vs, mock_emb, mock_session, health_test_config
    ):
        """Test health status returns healthy when components are healthy."""
        # Mock all components as healthy
        mock_session_instance = Mock()
        mock_session_instance.check_health.return_value = True
        mock_session.return_value = mock_session_instance

        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vs.return_value = mock_vs_instance
        mock_emb.return_value = Mock()

        service = HealthService(health_test_config)
        result = service.get_health_status()

        assert result.status == constants.HEALTH_STATUS_HEALTHY

    @patch("app.modules.health.service.SessionFactory")
    @patch("app.modules.health.service.create_embeddings")
    @patch("app.modules.health.service.create_vectorstore")
    def test_get_health_status_includes_components(
        self, mock_vs, mock_emb, mock_session, health_test_config
    ):
        """Test health status includes component array."""
        # Mock components
        mock_session_instance = Mock()
        mock_session_instance.check_health.return_value = True
        mock_session.return_value = mock_session_instance

        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vs.return_value = mock_vs_instance
        mock_emb.return_value = Mock()

        service = HealthService(health_test_config)
        result = service.get_health_status()

        assert hasattr(result, "components")
        assert len(result.components) == 4  # database, vectorstore, llm, embeddings
        component_names = [c.name for c in result.components]
        assert constants.COMPONENT_DATABASE in component_names
        assert constants.COMPONENT_VECTORSTORE in component_names

    @patch("app.modules.health.service.SessionFactory")
    @patch("app.modules.health.service.create_embeddings")
    @patch("app.modules.health.service.create_vectorstore")
    def test_get_health_status_includes_version(
        self, mock_vs, mock_emb, mock_session, health_test_config
    ):
        """Test health status includes API version."""
        # Mock components
        mock_session_instance = Mock()
        mock_session_instance.check_health.return_value = True
        mock_session.return_value = mock_session_instance

        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vs.return_value = mock_vs_instance
        mock_emb.return_value = Mock()

        service = HealthService(health_test_config)
        result = service.get_health_status()

        assert result.version is not None
        assert len(result.version) > 0

    @patch("app.modules.health.service.SessionFactory")
    @patch("app.modules.health.service.create_embeddings")
    @patch("app.modules.health.service.create_vectorstore")
    def test_get_health_status_with_database_type(
        self, mock_vs, mock_emb, mock_session, health_test_config
    ):
        """Test health status includes database type in details."""
        # Mock components
        mock_session_instance = Mock()
        mock_session_instance.check_health.return_value = True
        mock_session.return_value = mock_session_instance

        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vs.return_value = mock_vs_instance
        mock_emb.return_value = Mock()

        service = HealthService(health_test_config)
        result = service.get_health_status()

        # Find database component
        db_component = next(
            (c for c in result.components if c.name == constants.COMPONENT_DATABASE),
            None,
        )
        assert db_component is not None
        assert "type" in db_component.details
