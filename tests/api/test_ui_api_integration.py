"""
API-level UI integration tests.

Fast, reliable tests for UI endpoint accessibility without browser automation.
Tests the unified architecture where Streamlit UI is served via FastAPI.

UI INTEGRATION TESTS - These tests verify UI endpoints and Streamlit embedding.
They test route accessibility, iframe embedding, and configuration handling.

These tests are marked with @pytest.mark.ui and are skipped during
unit test runs. Run with: make test-ui-api

Test Coverage:
- UI route accessibility (/langchain/chat, /, /docs)
- iframe embedding when UI is available
- Error handling when UI is disabled
- Configuration validation (UIConfig)
- Constants verification (UI_ROUTE_*, UI_PAGE_*)
- Trace codes validation (UI_STREAMLIT_*, UI_QUERY_*)
- API + UI integration on same port
"""

import pytest

# Mark all tests in this module as UI integration tests
pytestmark = pytest.mark.ui

from unittest.mock import Mock, patch

import constants
import trace.codes as codes


@pytest.fixture
def mock_streamlit_process():
    """Mock Streamlit process for tests."""
    process = Mock()
    process.returncode = 0
    return process


class TestUIRouteAccessibility:
    """Test UI route accessibility and responses."""

    @patch("app.api.main.start_streamlit_ui")
    def test_root_redirects_to_docs(self, mock_start):
        """Test / redirects to /docs."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)
        response = client.get(constants.UI_ROUTE_ROOT, follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == constants.UI_ROUTE_DOCS

    @patch("app.api.main.start_streamlit_ui")
    def test_langchain_chat_returns_html(self, mock_start):
        """Test /langchain/chat returns HTML page."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)
        response = client.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

        assert "text/html" in response.headers["content-type"]

    @patch("app.api.main.start_streamlit_ui")
    @patch("app.api.main.streamlit_process")
    def test_ui_available_returns_iframe(self, mock_process, mock_start, mock_streamlit_process):
        """Test /langchain/chat returns iframe when UI is available."""
        mock_process.return_value = mock_streamlit_process

        from fastapi.testclient import TestClient
        from app.api.main import app

        with patch("app.api.main.streamlit_process", mock_streamlit_process):
            client = TestClient(app)
            response = client.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

            assert response.status_code == 200
            assert "<iframe" in response.text
            assert "8501" in response.text  # Streamlit port

    @patch("app.api.main.start_streamlit_ui")
    @patch("app.api.main.streamlit_process", None)
    def test_ui_unavailable_returns_warning(self, mock_start):
        """Test /langchain/chat returns 503 when UI is unavailable."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)
        response = client.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

        assert response.status_code == 503
        assert "Not Available" in response.text
        assert constants.UI_STREAMLIT_NOT_INSTALLED in response.text

    @patch("app.api.main.start_streamlit_ui")
    def test_ui_iframe_title(self, mock_start, mock_streamlit_process):
        """Test iframe page has correct title."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        with patch("app.api.main.streamlit_process", mock_streamlit_process):
            client = TestClient(app)
            response = client.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

            assert constants.UI_IFRAME_TITLE_LANGCHAIN in response.text

    @patch("app.api.main.start_streamlit_ui")
    def test_favicon_returns_204(self, mock_start):
        """Test /favicon.ico returns 204 No Content."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)
        response = client.get("/favicon.ico")

        assert response.status_code == 204


class TestUIConfiguration:
    """Test UI configuration handling."""

    def test_ui_config_exists(self):
        """Test UI configuration is loaded."""
        from config import Config

        config = Config()

        assert hasattr(config, "ui")
        assert config.ui is not None

    def test_ui_config_properties(self):
        """Test UI configuration has all required properties."""
        from config import Config

        config = Config()

        assert hasattr(config.ui, "enabled")
        assert hasattr(config.ui, "host")
        assert hasattr(config.ui, "port")
        assert hasattr(config.ui, "headless")
        assert hasattr(config.ui, "enable_cors")
        assert hasattr(config.ui, "enable_xsrf_protection")
        assert hasattr(config.ui, "startup_timeout")
        assert hasattr(config.ui, "shutdown_timeout")

    def test_ui_config_values(self):
        """Test UI configuration has sensible default values."""
        from config import Config

        config = Config()

        assert config.ui.port == 8501
        assert config.ui.host == "localhost"
        assert config.ui.headless is True
        assert config.ui.startup_timeout > 0
        assert config.ui.shutdown_timeout > 0


class TestUIConstants:
    """Test UI constants are properly defined."""

    def test_route_constants_defined(self):
        """Test UI route constants are defined."""
        assert hasattr(constants, "UI_ROUTE_LANGCHAIN_CHAT")
        assert hasattr(constants, "UI_ROUTE_LANGGRAPH_CHAT")
        assert hasattr(constants, "UI_ROUTE_ROOT")
        assert hasattr(constants, "UI_ROUTE_DOCS")

    def test_route_values(self):
        """Test UI route constants have correct values."""
        assert constants.UI_ROUTE_LANGCHAIN_CHAT == "/langchain/chat"
        assert constants.UI_ROUTE_LANGGRAPH_CHAT == "/langgraph/chat"
        assert constants.UI_ROUTE_ROOT == "/"
        assert constants.UI_ROUTE_DOCS == "/docs"

    def test_message_constants_defined(self):
        """Test UI message constants are defined."""
        assert hasattr(constants, "UI_STREAMLIT_NOT_INSTALLED")
        assert hasattr(constants, "UI_STREAMLIT_INSTALL_HINT")
        assert hasattr(constants, "UI_STREAMLIT_STARTUP_FAILED")
        assert hasattr(constants, "UI_STREAMLIT_SHUTDOWN_FAILED")

    def test_ui_config_constants_defined(self):
        """Test UI configuration constants are defined."""
        assert hasattr(constants, "UI_STREAMLIT_PORT")
        assert hasattr(constants, "UI_STREAMLIT_HOST")
        assert hasattr(constants, "UI_STREAMLIT_HEADLESS")

    def test_page_config_constants_defined(self):
        """Test UI page configuration constants are defined."""
        assert hasattr(constants, "UI_PAGE_TITLE")
        assert hasattr(constants, "UI_PAGE_ICON")
        assert hasattr(constants, "UI_LAYOUT")


class TestUITraceCodes:
    """Test UI trace codes are properly defined."""

    def test_lifecycle_trace_codes(self):
        """Test UI lifecycle trace codes are defined."""
        assert hasattr(codes, "UI_STREAMLIT_STARTING")
        assert hasattr(codes, "UI_STREAMLIT_STARTED")
        assert hasattr(codes, "UI_STREAMLIT_STOPPING")
        assert hasattr(codes, "UI_STREAMLIT_STOPPED")
        assert hasattr(codes, "UI_STREAMLIT_FAILED")

    def test_route_trace_codes(self):
        """Test UI route access trace codes are defined."""
        assert hasattr(codes, "UI_ROUTE_ACCESSED")
        assert hasattr(codes, "UI_LANGCHAIN_CHAT_ACCESSED")
        assert hasattr(codes, "UI_LANGGRAPH_CHAT_ACCESSED")

    def test_operation_trace_codes(self):
        """Test UI operation trace codes are defined."""
        assert hasattr(codes, "UI_QUERY_PROCESSING")
        assert hasattr(codes, "UI_QUERY_COMPLETED")
        assert hasattr(codes, "UI_QUERY_FAILED")
        assert hasattr(codes, "UI_FILE_UPLOAD_STARTED")
        assert hasattr(codes, "UI_FILE_UPLOAD_COMPLETED")


class TestAPIAndUIIntegration:
    """Test API and UI work together correctly."""

    @patch("app.api.main.start_streamlit_ui")
    def test_api_routes_still_accessible_with_ui(self, mock_start):
        """Test API routes remain accessible when UI is enabled."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)

        # Test API routes
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200

        docs_response = client.get("/docs")
        assert docs_response.status_code == 200

    @patch("app.api.main.start_streamlit_ui")
    def test_ui_and_api_use_same_port(self, mock_start):
        """Test UI and API are served from same port."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)

        # Both should work from same client (same port)
        api_response = client.get("/api/v1/health")
        ui_response = client.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

        assert api_response.status_code == 200
        assert ui_response.status_code in [200, 503]  # 503 if UI disabled

    @patch("app.api.main.start_streamlit_ui")
    def test_root_to_docs_redirection_works(self, mock_start):
        """Test root redirect to docs works correctly."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)

        # Follow redirect
        response = client.get("/", follow_redirects=True)

        assert response.status_code == 200
        assert "FastAPI" in response.text or "Swagger" in response.text


class TestErrorHandling:
    """Test error handling in UI routes."""

    @patch("app.api.main.start_streamlit_ui")
    @patch("app.api.main.streamlit_process", None)
    def test_ui_disabled_error_message(self, mock_start):
        """Test error message when UI is disabled."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)
        response = client.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

        assert response.status_code == 503
        assert "UI Not Available" in response.text
        assert "pip install streamlit" in response.text

    @patch("app.api.main.start_streamlit_ui")
    def test_404_for_unknown_routes(self, mock_start):
        """Test 404 returned for unknown routes."""
        from fastapi.testclient import TestClient
        from app.api.main import app

        client = TestClient(app)
        response = client.get("/unknown/route/here")

        assert response.status_code == 404

