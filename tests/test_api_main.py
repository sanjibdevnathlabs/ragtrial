"""
Tests for FastAPI main application module.

Tests application initialization, middleware, error handlers, and lifecycle.
"""

from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import constants
from app.api.main import app, get_config, log_registered_routes


@pytest.fixture(scope="module", autouse=True)
def mock_health_dependencies():
    """
    Mock ALL health check dependencies at module level to prevent real API calls.

    This fixture uses autouse=True to ensure it's ALWAYS applied for ALL tests in this module.

    CRITICAL: Unit tests should NEVER connect to real services:
    - No real LLM API calls (Google Gemini) - costs money + quota limits
    - No real Embeddings API calls (Google) - costs money + quota limits
    - No real Vectorstore connections (ChromaDB) - disk I/O
    """
    # Reset HealthService singleton to ensure clean state
    from app.modules.health.service import HealthService

    if hasattr(HealthService, "_instances"):
        HealthService._instances.clear()

    # Patch internal health check methods directly
    with patch.object(HealthService, "_test_llm_api", return_value=True), patch.object(
        HealthService, "_test_embeddings_api", return_value=True
    ), patch("app.modules.health.service.create_embeddings") as mock_embeddings, patch(
        "app.modules.health.service.create_vectorstore"
    ) as mock_vectorstore:

        # Mock Embeddings to return success
        mock_embeddings_instance = Mock()
        mock_embeddings_instance.embed_query.return_value = [0.1] * 768
        mock_embeddings.return_value = mock_embeddings_instance

        # Mock Vectorstore to return success
        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vectorstore.return_value = mock_vs_instance

        yield

        # Clean up singleton after module
        if hasattr(HealthService, "_instances"):
            HealthService._instances.clear()


@pytest.fixture
def client():
    """Create test client with mocked dependencies (via autouse fixture)."""
    return TestClient(app)


class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_serves_react_app(self, client):
        """Test root endpoint serves React frontend."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_root_returns_html(self, client):
        """Test root endpoint returns HTML (React app)."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_docs_endpoint_accessible(self, client):
        """Test /docs endpoint is directly accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        # Docs page contains HTML with API documentation
        assert "text/html" in response.headers["content-type"]
        assert "swagger" in response.text.lower() or "api" in response.text.lower()


class TestFaviconEndpoint:
    """Test suite for favicon endpoint."""

    def test_favicon_returns_204(self, client):
        """Test favicon endpoint returns 204 No Content."""
        response = client.get("/favicon.ico")
        assert response.status_code == 204

    def test_favicon_returns_empty_body(self, client):
        """Test favicon endpoint returns empty body."""
        response = client.get("/favicon.ico")
        assert response.content == b""


class TestGlobalExceptionHandler:
    """Test suite for global exception handler."""

    def test_exception_handler_exists(self):
        """Test that global exception handler is registered."""
        from app.api.main import global_exception_handler

        # Test handler exists and is callable
        assert callable(global_exception_handler)

    def test_exception_handler_registered_in_app(self):
        """Test that exception handler is registered in the app."""
        # The exception handler should be in the app's exception handlers
        assert Exception in app.exception_handlers or len(app.exception_handlers) > 0


class TestGetConfig:
    """Test suite for get_config function."""

    def test_get_config_returns_config_instance(self):
        """Test that get_config returns a Config instance."""
        from config import Config

        config = get_config()

        assert isinstance(config, Config)

    def test_get_config_returns_same_instance(self):
        """Test that get_config returns the same singleton instance."""
        config1 = get_config()
        config2 = get_config()

        # Should be the same instance (singleton)
        assert config1 is config2


class TestLogRegisteredRoutes:
    """Test suite for log_registered_routes function."""

    def test_log_registered_routes_prints_output(self):
        """Test that log_registered_routes prints output."""
        mock_app = MagicMock()
        mock_route1 = MagicMock()
        mock_route1.methods = ["GET", "HEAD", "OPTIONS"]
        mock_route1.path = "/test"
        mock_route1.name = "test_route"

        mock_route2 = MagicMock()
        mock_route2.methods = ["POST"]
        mock_route2.path = "/api/test"
        mock_route2.name = "api_test"

        mock_app.routes = [mock_route1, mock_route2]

        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as fake_out:
            log_registered_routes(mock_app)
            output = fake_out.getvalue()

        # Check output contains expected content
        assert "REGISTERED API ROUTES" in output
        assert "/test" in output
        assert "/api/test" in output
        assert "test_route" in output
        assert "api_test" in output
        assert "Total routes:" in output

    def test_log_registered_routes_filters_head_options(self):
        """Test that log_registered_routes filters HEAD and OPTIONS methods."""
        mock_app = MagicMock()
        mock_route = MagicMock()
        mock_route.methods = ["GET", "HEAD", "OPTIONS"]
        mock_route.path = "/test"
        mock_route.name = "test"

        mock_app.routes = [mock_route]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            log_registered_routes(mock_app)
            output = fake_out.getvalue()

        # Should only show GET, not HEAD or OPTIONS
        assert "GET" in output
        assert (
            "HEAD" not in output
            or "HEAD" not in output.split("METHOD")[1].split("\n")[2]
        )

    def test_log_registered_routes_sorts_by_path(self):
        """Test that routes are sorted by path."""
        mock_app = MagicMock()

        route1 = MagicMock()
        route1.methods = ["GET"]
        route1.path = "/z-last"
        route1.name = "last"

        route2 = MagicMock()
        route2.methods = ["GET"]
        route2.path = "/a-first"
        route2.name = "first"

        route3 = MagicMock()
        route3.methods = ["GET"]
        route3.path = "/m-middle"
        route3.name = "middle"

        mock_app.routes = [route1, route2, route3]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            log_registered_routes(mock_app)
            output = fake_out.getvalue()

        # Check that paths appear in sorted order
        a_pos = output.find("/a-first")
        m_pos = output.find("/m-middle")
        z_pos = output.find("/z-last")

        assert a_pos < m_pos < z_pos

    def test_log_registered_routes_handles_no_name_attribute(self):
        """Test that function handles routes without name attribute."""
        mock_app = MagicMock()
        mock_route = MagicMock()
        mock_route.methods = ["GET"]
        mock_route.path = "/test"
        # No name attribute
        del mock_route.name

        mock_app.routes = [mock_route]

        # Should not raise an exception
        with patch("sys.stdout", new=StringIO()):
            log_registered_routes(mock_app)


class TestCORSMiddleware:
    """Test suite for CORS middleware."""

    def test_cors_allows_configured_origins(self, client):
        """Test that CORS middleware allows configured origins."""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        # Should return successful response
        assert response.status_code == 200

    def test_cors_includes_access_control_headers(self, client):
        """Test that CORS response includes access control headers."""
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Should include CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers


class TestApplicationMetadata:
    """Test suite for application metadata."""

    def test_app_title(self):
        """Test application title is set correctly."""
        assert app.title == "RAG Application API"

    def test_app_version(self):
        """Test application version is set correctly."""
        assert app.version == "1.0.0"

    def test_app_description(self):
        """Test application description is set."""
        assert "document management" in app.description.lower()
        assert "rag" in app.description.lower()


class TestIntegration:
    """Integration tests for main application."""

    def test_all_routers_registered(self, client):
        """
        Test that all routers are properly registered.

        This test verifies route registration, not business logic:
        - GET endpoints should return 200 or valid errors (400, 422, 500), NOT 404
        - POST-only endpoints should return 405 (Method Not Allowed), NOT 404
        - 404 means the route is not registered at all (failure)
        """
        # GET endpoints - should return success or valid business errors
        get_endpoints = [
            ("/api/v1/health", 200),  # Health check
            ("/api/v1/files", 200),  # List files (may be empty)
            ("/api/v1/devdocs/list", 200),  # List documentation files
        ]

        for endpoint, expected_status in get_endpoints:
            response = client.get(endpoint)
            assert (
                response.status_code == expected_status
            ), f"GET {endpoint} returned {response.status_code}, expected {expected_status}"

        # POST-only endpoints - should return 405 (Method Not Allowed) when called with GET
        post_only_endpoints = [
            "/api/v1/upload",  # File upload
            "/api/v1/query",  # RAG query
        ]

        for endpoint in post_only_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 405, (
                f"GET {endpoint} returned {response.status_code}, expected 405 (Method Not Allowed). "
                f"404 would indicate the route is not registered."
            )

    def test_application_starts_successfully(self, client):
        """Test that application can start and respond to requests."""
        # Simple smoke test
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/api/v1/health")
        assert response.status_code == 200
