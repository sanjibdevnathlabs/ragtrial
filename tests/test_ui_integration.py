"""
Integration tests for UI embedding in FastAPI.

Tests Streamlit subprocess management and UI route accessibility.
"""

import subprocess
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import constants
import trace.codes as codes


@pytest.fixture
def mock_streamlit_process():
    """Mock Streamlit subprocess."""
    mock_process = Mock(spec=subprocess.Popen)
    mock_process.returncode = 0
    mock_process.terminate = Mock()
    mock_process.wait = Mock()
    mock_process.kill = Mock()
    return mock_process


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for streamlit --version check."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Streamlit, version 1.50.0"
    return mock_result


@pytest.fixture
def mock_subprocess_popen(mock_streamlit_process):
    """Mock subprocess.Popen for streamlit run."""
    return Mock(return_value=mock_streamlit_process)


class TestStreamlitLifecycle:
    """Test Streamlit subprocess lifecycle management."""

    @patch("app.api.main.subprocess.run")
    @patch("app.api.main.subprocess.Popen")
    def test_start_streamlit_success(
        self,
        mock_popen,
        mock_run,
        mock_subprocess_popen,
        mock_subprocess_run,
    ):
        """Test successful Streamlit startup."""
        mock_run.return_value = mock_subprocess_run
        mock_popen.return_value = mock_subprocess_popen.return_value

        # Import after mocking
        from app.api.main import start_streamlit_ui, streamlit_process

        start_streamlit_ui()

        # Verify streamlit --version was called
        mock_run.assert_called_once()
        assert "streamlit" in mock_run.call_args[0][0]
        assert "--version" in mock_run.call_args[0][0]

        # Verify streamlit run was called
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert "streamlit" in args
        assert "run" in args
        assert "app/ui/main.py" in args

    @patch("app.api.main.subprocess.run")
    def test_start_streamlit_not_installed(self, mock_run):
        """Test Streamlit not installed scenario."""
        mock_run.side_effect = FileNotFoundError("streamlit not found")

        # Import after mocking
        from app.api.main import start_streamlit_ui

        # Should not raise, just log warning
        start_streamlit_ui()

        mock_run.assert_called_once()

    @patch("app.api.main.subprocess.run")
    @patch("app.api.main.subprocess.Popen")
    def test_stop_streamlit_graceful(
        self,
        mock_popen,
        mock_run,
        mock_subprocess_popen,
        mock_subprocess_run,
    ):
        """Test graceful Streamlit shutdown."""
        mock_run.return_value = mock_subprocess_run
        mock_popen.return_value = mock_subprocess_popen.return_value

        # Import and start
        from app.api.main import start_streamlit_ui, stop_streamlit_ui

        start_streamlit_ui()
        mock_process = mock_popen.return_value

        # Stop
        stop_streamlit_ui()

        # Verify graceful termination
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
        assert mock_process.kill.call_count == 0

    @patch("app.api.main.subprocess.run")
    @patch("app.api.main.subprocess.Popen")
    def test_stop_streamlit_force_kill(
        self,
        mock_popen,
        mock_run,
        mock_subprocess_popen,
        mock_subprocess_run,
    ):
        """Test forced Streamlit shutdown on timeout."""
        mock_run.return_value = mock_subprocess_run
        mock_popen.return_value = mock_subprocess_popen.return_value

        # Make first wait() raise timeout, second wait() (after kill) succeed
        mock_process = mock_popen.return_value
        mock_process.wait.side_effect = [
            subprocess.TimeoutExpired("streamlit", 5),  # First wait() times out
            None,  # Second wait() (after kill) succeeds
        ]

        # Import and start
        from app.api.main import start_streamlit_ui, stop_streamlit_ui

        start_streamlit_ui()

        # Stop (should force kill)
        stop_streamlit_ui()

        # Verify force kill was called
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
        # Verify wait was called twice (graceful + after kill)
        assert mock_process.wait.call_count == 2


class TestUIRoutes:
    """Test UI route accessibility."""

    @pytest.fixture
    def client(self):
        """Create test client without starting Streamlit."""
        # Mock streamlit process to None (not started)
        with patch("app.api.main.start_streamlit_ui"):
            from app.api.main import app

            return TestClient(app)

    def test_root_serves_react_app(self, client):
        """Test root route serves React frontend."""
        response = client.get(constants.UI_ROUTE_ROOT, follow_redirects=False)

        assert response.status_code == 200  # Serves React app
        assert "text/html" in response.headers.get("content-type", "")

    def test_langchain_chat_ui_not_available(self, client):
        """Test /langchain/chat when Streamlit not available."""
        with patch("app.api.main.streamlit_process", None):
            response = client.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

            assert response.status_code == 503
            assert constants.UI_STREAMLIT_NOT_INSTALLED in response.text

    @patch("app.api.main.streamlit_process")
    def test_langchain_chat_ui_available(self, mock_process, client):
        """Test /langchain/chat when Streamlit is available."""
        # Mock streamlit process as running
        mock_process.return_value = Mock(spec=subprocess.Popen)

        from app.api.main import app
        from config import Config

        config = Config()

        with patch("app.api.main.streamlit_process", mock_process):
            with patch("app.api.main.get_config", return_value=config):
                client_with_ui = TestClient(app)
                response = client_with_ui.get(constants.UI_ROUTE_LANGCHAIN_CHAT)

                assert response.status_code == 200
                assert "<iframe" in response.text
                assert f"http://{config.ui.host}:{config.ui.port}" in response.text


class TestUIConfiguration:
    """Test UI configuration handling."""

    @patch("app.api.main.subprocess.run")
    @patch("app.api.main.subprocess.Popen")
    def test_ui_disabled_in_config(self, mock_popen, mock_run):
        """Test Streamlit not started when disabled in config."""
        from config import Config

        config = Config()
        original_enabled = config.ui.enabled
        config.ui.enabled = False

        try:
            from app.api.main import start_streamlit_ui

            start_streamlit_ui()

            # Verify streamlit was NOT started
            mock_run.assert_not_called()
            mock_popen.assert_not_called()

        finally:
            config.ui.enabled = original_enabled

    @patch("app.api.main.subprocess.run")
    @patch("app.api.main.subprocess.Popen")
    def test_ui_config_values_used(
        self,
        mock_popen,
        mock_run,
        mock_subprocess_run,
        mock_subprocess_popen,
    ):
        """Test UI configuration values are used in subprocess call."""
        mock_run.return_value = mock_subprocess_run
        mock_popen.return_value = mock_subprocess_popen

        from app.api.main import start_streamlit_ui
        from config import Config

        config = Config()

        start_streamlit_ui()

        # Verify config values are used
        args = mock_popen.call_args[0][0]
        assert str(config.ui.port) in args
        assert str(config.ui.headless).lower() in args


class TestUIIntegrationFlow:
    """Test complete UI integration flow."""

    @patch("app.api.main.subprocess.run")
    @patch("app.api.main.subprocess.Popen")
    def test_full_startup_shutdown_flow(
        self,
        mock_popen,
        mock_run,
        mock_subprocess_popen,
        mock_subprocess_run,
    ):
        """Test complete startup and shutdown flow."""
        mock_run.return_value = mock_subprocess_run
        mock_popen.return_value = mock_subprocess_popen.return_value

        from app.api.main import start_streamlit_ui, stop_streamlit_ui

        # Startup
        start_streamlit_ui()
        assert mock_popen.called

        # Shutdown
        stop_streamlit_ui()
        mock_process = mock_popen.return_value
        assert mock_process.terminate.called
