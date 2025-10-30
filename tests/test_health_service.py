"""
Unit tests for health service.

Tests all health check functionality including database, vectorstore,
LLM, and embeddings health checks with caching.
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

import constants
from app.modules.health.service import HealthService
from config import Config


@pytest.fixture
def config():
    """Config fixture for tests."""
    return Config()


@pytest.fixture
def health_service(config):
    """Health service fixture."""
    return HealthService(config)


class TestHealthServiceInitialization:
    """Test health service initialization."""

    def test_health_service_singleton(self, config):
        """Test that HealthService is a singleton."""
        service1 = HealthService(config)
        service2 = HealthService(config)

        assert service1 is service2

    def test_health_service_has_config(self, health_service, config):
        """Test that health service has config."""
        assert health_service.config is config

    def test_health_service_cache_initialization(self, health_service):
        """Test that caches are initialized to None."""
        assert health_service._llm_health_cache is None
        assert health_service._embeddings_health_cache is None


class TestDatabaseHealthCheck:
    """Test database health checks."""

    def test_check_database_healthy(self, health_service):
        """Test database health check when database is healthy."""
        with patch.object(health_service, "_check_database_health") as mock_check:
            mock_check.return_value = (True, {"type": "mysql"})

            is_healthy, details = health_service._check_database_health()

            assert is_healthy is True
            assert details["type"] == "mysql"

    def test_check_database_unhealthy(self, health_service):
        """Test database health check when database is unhealthy."""
        with patch("app.modules.health.service.SessionFactory") as mock_factory:
            mock_instance = Mock()
            mock_instance.check_health.return_value = False
            mock_factory.return_value = mock_instance

            is_healthy, details = health_service._check_database_health()

            assert is_healthy is False

    def test_check_database_exception_handling(self, health_service):
        """Test database health check handles exceptions."""
        with patch("app.modules.health.service.SessionFactory") as mock_factory:
            mock_instance = Mock()
            mock_instance.check_health.side_effect = Exception(
                "Database connection failed"
            )
            mock_factory.return_value = mock_instance

            is_healthy, details = health_service._check_database_health()

            assert is_healthy is False
            assert "error" in details


class TestVectorstoreHealthCheck:
    """Test vectorstore health checks."""

    def test_check_vectorstore_healthy(self, health_service):
        """Test vectorstore health check when vectorstore is healthy."""
        with patch(
            "app.modules.health.service.create_embeddings"
        ) as mock_embeddings, patch(
            "app.modules.health.service.create_vectorstore"
        ) as mock_vs:
            mock_vs_instance = Mock()
            mock_vs_instance.check_health.return_value = True
            mock_vs.return_value = mock_vs_instance
            mock_embeddings.return_value = Mock()

            is_healthy, details = health_service._check_vectorstore_health()

            assert is_healthy is True
            assert details["provider"] == health_service.config.vectorstore.provider

    def test_check_vectorstore_unhealthy(self, health_service):
        """Test vectorstore health check when vectorstore is unhealthy."""
        with patch(
            "app.modules.health.service.create_embeddings"
        ) as mock_embeddings, patch(
            "app.modules.health.service.create_vectorstore"
        ) as mock_vs:
            mock_vs_instance = Mock()
            mock_vs_instance.check_health.return_value = False
            mock_vs.return_value = mock_vs_instance
            mock_embeddings.return_value = Mock()

            is_healthy, details = health_service._check_vectorstore_health()

            assert is_healthy is False

    def test_check_vectorstore_exception_handling(self, health_service):
        """Test vectorstore health check handles exceptions."""
        with patch("app.modules.health.service.create_embeddings") as mock_embeddings:
            mock_embeddings.side_effect = Exception("Embeddings creation failed")

            is_healthy, details = health_service._check_vectorstore_health()

            assert is_healthy is False
            assert "error" in details


class TestLLMHealthCheck:
    """Test LLM health checks with caching."""

    def test_llm_health_check_fresh(self, health_service):
        """Test LLM health check with fresh API call."""
        with patch.object(health_service, "_test_llm_api") as mock_test:
            mock_test.return_value = True

            is_healthy, details = health_service._check_llm_health_cached()

            assert is_healthy is True
            assert details["provider"] == health_service.config.rag.provider
            assert details["cached"] == "false"

    def test_llm_health_check_cached(self, health_service):
        """Test LLM health check with cached result."""
        # Set cache
        current_time = time.time()
        health_service._llm_health_cache = (True, current_time)

        is_healthy, details = health_service._check_llm_health_cached()

        assert is_healthy is True
        assert details["cached"] == "true"
        assert "cache_age_seconds" in details

    def test_llm_health_check_cache_expiry(self, health_service):
        """Test LLM health check cache expiry."""
        # Set expired cache (61 seconds ago)
        expired_time = time.time() - (constants.HEALTH_CHECK_CACHE_DURATION + 1)
        health_service._llm_health_cache = (True, expired_time)

        with patch.object(health_service, "_test_llm_api") as mock_test:
            mock_test.return_value = True

            is_healthy, details = health_service._check_llm_health_cached()

            # Should make fresh API call
            assert details["cached"] == "false"
            mock_test.assert_called_once()

    def test_llm_health_check_failure_cached(self, health_service):
        """Test LLM health check caches failures too."""
        with patch.object(health_service, "_test_llm_api") as mock_test:
            mock_test.return_value = False

            is_healthy, details = health_service._check_llm_health_cached()

            assert is_healthy is False

            # Check cache was updated
            assert health_service._llm_health_cache is not None
            assert health_service._llm_health_cache[0] is False

    def test_test_llm_api_success(self, health_service):
        """Test LLM API test with successful response."""
        with patch("llm.factory.create_llm") as mock_create:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Test response"
            mock_llm.invoke.return_value = mock_response
            mock_create.return_value = mock_llm

            result = health_service._test_llm_api()

            assert result is True
            mock_llm.invoke.assert_called_once_with("Hi")

    def test_test_llm_api_failure(self, health_service):
        """Test LLM API test with failure."""
        with patch("llm.factory.create_llm") as mock_create:
            mock_create.side_effect = Exception("LLM creation failed")

            result = health_service._test_llm_api()

            assert result is False

    def test_test_llm_api_empty_response(self, health_service):
        """Test LLM API test with empty response."""
        with patch("llm.factory.create_llm") as mock_create:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = ""
            mock_llm.invoke.return_value = mock_response
            mock_create.return_value = mock_llm

            result = health_service._test_llm_api()

            assert result is False


class TestEmbeddingsHealthCheck:
    """Test embeddings health checks with caching."""

    def test_embeddings_health_check_fresh(self, health_service):
        """Test embeddings health check with fresh API call."""
        with patch.object(health_service, "_test_embeddings_api") as mock_test:
            mock_test.return_value = True

            is_healthy, details = health_service._check_embeddings_health_cached()

            assert is_healthy is True
            assert details["provider"] == health_service.config.embeddings.provider
            assert details["cached"] == "false"

    def test_embeddings_health_check_cached(self, health_service):
        """Test embeddings health check with cached result."""
        # Set cache
        current_time = time.time()
        health_service._embeddings_health_cache = (True, current_time)

        is_healthy, details = health_service._check_embeddings_health_cached()

        assert is_healthy is True
        assert details["cached"] == "true"
        assert "cache_age_seconds" in details

    def test_embeddings_health_check_cache_expiry(self, health_service):
        """Test embeddings health check cache expiry."""
        # Set expired cache
        expired_time = time.time() - (constants.HEALTH_CHECK_CACHE_DURATION + 1)
        health_service._embeddings_health_cache = (True, expired_time)

        with patch.object(health_service, "_test_embeddings_api") as mock_test:
            mock_test.return_value = True

            is_healthy, details = health_service._check_embeddings_health_cached()

            # Should make fresh API call
            assert details["cached"] == "false"
            mock_test.assert_called_once()

    def test_test_embeddings_api_success(self, health_service):
        """Test embeddings API test with successful response."""
        with patch("embeddings.factory.create_embeddings") as mock_create:
            mock_embeddings = Mock()
            mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_create.return_value = mock_embeddings

            result = health_service._test_embeddings_api()

            assert result is True
            mock_embeddings.embed_query.assert_called_once_with("hi")

    def test_test_embeddings_api_failure(self, health_service):
        """Test embeddings API test with failure."""
        with patch("embeddings.factory.create_embeddings") as mock_create:
            mock_create.side_effect = Exception("Embeddings creation failed")

            result = health_service._test_embeddings_api()

            assert result is False

    def test_test_embeddings_api_empty_result(self, health_service):
        """Test embeddings API test with empty result."""
        with patch("embeddings.factory.create_embeddings") as mock_create:
            mock_embeddings = Mock()
            mock_embeddings.embed_query.return_value = []
            mock_create.return_value = mock_embeddings

            result = health_service._test_embeddings_api()

            assert result is False


class TestOverallHealthStatus:
    """Test overall health status determination."""

    def test_all_components_healthy(self, health_service):
        """Test overall status when all components are healthy."""
        with patch.object(
            health_service, "_check_database_health"
        ) as mock_db, patch.object(
            health_service, "_check_vectorstore_health"
        ) as mock_vs, patch.object(
            health_service, "_check_llm_health_cached"
        ) as mock_llm, patch.object(
            health_service, "_check_embeddings_health_cached"
        ) as mock_emb:
            mock_db.return_value = (True, {"type": "mysql"})
            mock_vs.return_value = (True, {"provider": "chroma"})
            mock_llm.return_value = (True, {"provider": "google", "cached": "false"})
            mock_emb.return_value = (True, {"provider": "google", "cached": "false"})

            health_response = health_service.get_health_status()

            assert health_response.status == constants.HEALTH_STATUS_HEALTHY
            assert len(health_response.components) == 4

    def test_critical_component_unhealthy(self, health_service):
        """Test overall status when critical component (database) is unhealthy."""
        with patch.object(
            health_service, "_check_database_health"
        ) as mock_db, patch.object(
            health_service, "_check_vectorstore_health"
        ) as mock_vs, patch.object(
            health_service, "_check_llm_health_cached"
        ) as mock_llm, patch.object(
            health_service, "_check_embeddings_health_cached"
        ) as mock_emb:
            mock_db.return_value = (False, {"error": "Connection failed"})
            mock_vs.return_value = (True, {"provider": "chroma"})
            mock_llm.return_value = (True, {"provider": "google", "cached": "false"})
            mock_emb.return_value = (True, {"provider": "google", "cached": "false"})

            health_response = health_service.get_health_status()

            assert health_response.status == constants.HEALTH_STATUS_UNHEALTHY

    def test_dependency_unhealthy_overall_healthy(self, health_service):
        """Test overall status when only dependency (LLM) is unhealthy."""
        with patch.object(
            health_service, "_check_database_health"
        ) as mock_db, patch.object(
            health_service, "_check_vectorstore_health"
        ) as mock_vs, patch.object(
            health_service, "_check_llm_health_cached"
        ) as mock_llm, patch.object(
            health_service, "_check_embeddings_health_cached"
        ) as mock_emb:
            mock_db.return_value = (True, {"type": "mysql"})
            mock_vs.return_value = (True, {"provider": "chroma"})
            mock_llm.return_value = (
                False,
                {"provider": "google", "error": "API failure"},
            )
            mock_emb.return_value = (True, {"provider": "google", "cached": "false"})

            health_response = health_service.get_health_status()

            # Overall should still be healthy (LLM is dependency, not critical)
            assert health_response.status == constants.HEALTH_STATUS_HEALTHY

            # But LLM component should show unhealthy
            llm_component = next(
                (
                    c
                    for c in health_response.components
                    if c.name == constants.COMPONENT_LLM
                ),
                None,
            )
            assert llm_component is not None
            assert llm_component.status == "unhealthy"

    def test_component_details_structure(self, health_service):
        """Test that component details have correct structure."""
        with patch.object(
            health_service, "_check_database_health"
        ) as mock_db, patch.object(
            health_service, "_check_vectorstore_health"
        ) as mock_vs, patch.object(
            health_service, "_check_llm_health_cached"
        ) as mock_llm, patch.object(
            health_service, "_check_embeddings_health_cached"
        ) as mock_emb:
            mock_db.return_value = (True, {"type": "mysql"})
            mock_vs.return_value = (True, {"provider": "chroma"})
            mock_llm.return_value = (True, {"provider": "google", "cached": "true"})
            mock_emb.return_value = (True, {"provider": "google", "cached": "true"})

            health_response = health_service.get_health_status()

            # Check all components present
            component_names = [c.name for c in health_response.components]
            assert constants.COMPONENT_DATABASE in component_names
            assert constants.COMPONENT_VECTORSTORE in component_names
            assert constants.COMPONENT_LLM in component_names
            assert constants.COMPONENT_EMBEDDINGS in component_names

            # Check categories
            for component in health_response.components:
                assert component.category in [
                    constants.COMPONENT_CATEGORY_CRITICAL,
                    constants.COMPONENT_CATEGORY_DEPENDENCY,
                ]


class TestCacheBehavior:
    """Test caching behavior across multiple health checks."""

    def test_cache_persists_across_calls(self, health_service):
        """Test that cache persists across multiple health check calls."""
        with patch.object(health_service, "_test_llm_api") as mock_test:
            mock_test.return_value = True

            # First call - fresh
            health_service._check_llm_health_cached()
            assert mock_test.call_count == 1

            # Second call - should use cache
            health_service._check_llm_health_cached()
            assert mock_test.call_count == 1  # Still 1, not called again

    def test_independent_caches_for_llm_and_embeddings(self, health_service):
        """Test that LLM and embeddings have independent caches."""
        with patch.object(
            health_service, "_test_llm_api"
        ) as mock_llm_test, patch.object(
            health_service, "_test_embeddings_api"
        ) as mock_emb_test:
            mock_llm_test.return_value = True
            mock_emb_test.return_value = True

            # Check LLM
            health_service._check_llm_health_cached()

            # Check embeddings
            health_service._check_embeddings_health_cached()

            # Both should have been called once
            assert mock_llm_test.call_count == 1
            assert mock_emb_test.call_count == 1

            # Caches should be independent
            assert health_service._llm_health_cache is not None
            assert health_service._embeddings_health_cache is not None
            assert (
                health_service._llm_health_cache
                != health_service._embeddings_health_cache
            )
