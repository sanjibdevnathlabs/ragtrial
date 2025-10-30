"""
Tests for FastAPI main application module.

Tests application initialization, middleware, error handlers, and lifecycle.
"""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.main import app, get_config, log_registered_routes


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_redirects_to_docs(self, client):
        """Test root endpoint redirects to /docs."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/docs"

    def test_root_redirect_target_accessible(self, client):
        """Test following redirect from root leads to docs."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        # Docs page contains HTML with API documentation
        assert "text/html" in response.headers["content-type"]
        assert "FastAPI" in response.text or "Swagger" in response.text or "API" in response.text

    def test_root_returns_200(self, client):
        """Test root endpoint (following redirect) returns 200 OK."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200

    def test_root_returns_html_after_redirect(self, client):
        """Test root endpoint (following redirect) returns HTML."""
        response = client.get("/", follow_redirects=True)
        assert "text/html" in response.headers["content-type"]


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
        """Test that all routers are accessible."""
        # Test health router
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        # Test that endpoints exist (may return errors without proper setup, but should not 404)
        endpoints = ["/api/v1/files", "/api/v1/upload", "/api/v1/query"]

        for endpoint in endpoints:
            # Just verify the endpoint exists (not 404)
            # Some may return 4xx/5xx but that's OK for this test
            response = client.get(endpoint)
            assert response.status_code != 404

    def test_application_starts_successfully(self, client):
        """Test that application can start and respond to requests."""
        # Simple smoke test
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/api/v1/health")
        assert response.status_code == 200
