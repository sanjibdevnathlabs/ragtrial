"""
Router tests for devdocs endpoint.

Tests the FastAPI router layer with proper request/response handling.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module", autouse=True)
def mock_health_dependencies():
    """Mock health check dependencies to prevent real API calls."""
    from app.modules.health.service import HealthService
    from database.session import SessionFactory

    if hasattr(HealthService, "_instances"):
        HealthService._instances.clear()
    if hasattr(SessionFactory, "_instances"):
        SessionFactory._instances.clear()

    with patch.object(HealthService, "_test_llm_api", return_value=True), patch.object(
        HealthService, "_test_embeddings_api", return_value=True
    ), patch("app.modules.health.service.create_embeddings") as mock_embeddings, patch(
        "app.modules.health.service.create_vectorstore"
    ) as mock_vectorstore, patch(
        "database.session.SessionFactory.check_health", return_value=True
    ), patch(
        "database.session.SessionFactory.get_read_session"
    ) as mock_read_session:

        mock_embeddings_instance = Mock()
        mock_embeddings_instance.embed_query.return_value = [0.1] * 768
        mock_embeddings.return_value = mock_embeddings_instance

        mock_vs_instance = Mock()
        mock_vs_instance.check_health.return_value = True
        mock_vectorstore.return_value = mock_vs_instance

        mock_session = Mock()
        mock_query_chain = Mock()
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.order_by.return_value = mock_query_chain
        mock_query_chain.limit.return_value = mock_query_chain
        mock_query_chain.offset.return_value = mock_query_chain
        mock_query_chain.all.return_value = []
        mock_query_chain.first.return_value = None
        mock_session.query.return_value = mock_query_chain
        mock_read_session.return_value.__enter__.return_value = mock_session
        mock_read_session.return_value.__exit__.return_value = None

        yield

        if hasattr(HealthService, "_instances"):
            HealthService._instances.clear()
        if hasattr(SessionFactory, "_instances"):
            SessionFactory._instances.clear()


@pytest.fixture
def client():
    """Create test client."""
    from app.api.main import app

    return TestClient(app)


@pytest.fixture
def mock_project_root(tmp_path):
    """Create a mock project root with documentation files."""
    # Create README.md
    readme = tmp_path / "README.md"
    readme.write_text("# Project README\n\nThis is the main README.")

    # Create docs directory with markdown files
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "guide.md").write_text("# User Guide\n\nHow to use this project.")
    (docs_dir / "api.md").write_text("# API Reference\n\nAPI documentation.")

    # Create examples directory with Python files
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    (examples_dir / "example1.py").write_text("# Example 1\nprint('Hello')")
    (examples_dir / "example2.py").write_text("# Example 2\nprint('World')")

    return tmp_path


class TestDevDocsRouterList:
    """Test documentation file listing via router."""

    def test_list_docs_success(self, client, mock_project_root):
        """Test successful documentation listing."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/list")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 5  # 1 README + 2 docs + 2 examples

            # Check README
            readme = next(d for d in data if d["name"] == "README.md")
            assert readme["path"] == "README.md"
            assert readme["type"] == "markdown"
            assert readme["category"] == "root"

            # Check docs
            docs = [d for d in data if d["category"] == "docs"]
            assert len(docs) == 2
            assert any(d["name"] == "guide.md" for d in docs)

            # Check examples
            examples = [d for d in data if d["category"] == "examples"]
            assert len(examples) == 2
            assert any(d["name"] == "example1.py" for d in examples)

            # Check Cache-Control header
            assert response.headers["Cache-Control"] == "no-cache, must-revalidate"

    def test_list_docs_empty_project(self, client, tmp_path):
        """Test listing docs in empty project."""
        with patch("app.routers.devdocs.get_project_root", return_value=tmp_path):
            response = client.get("/api/v1/devdocs/list")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

    def test_list_docs_only_readme(self, client, tmp_path):
        """Test listing docs with only README."""
        readme = tmp_path / "README.md"
        readme.write_text("# README")

        with patch("app.routers.devdocs.get_project_root", return_value=tmp_path):
            response = client.get("/api/v1/devdocs/list")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "README.md"


class TestDevDocsRouterContent:
    """Test documentation content retrieval via router."""

    def test_get_content_readme_success(self, client, mock_project_root):
        """Test successful README content retrieval."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/content?file_path=README.md")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "README.md"
            assert data["path"] == "README.md"
            assert data["type"] == "markdown"
            assert "Project README" in data["content"]

            # Check Cache-Control header
            assert response.headers["Cache-Control"] == "no-cache, must-revalidate"

    def test_get_content_docs_file_success(self, client, mock_project_root):
        """Test successful docs file content retrieval."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/content?file_path=docs/guide.md")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "guide.md"
            assert data["path"] == "docs/guide.md"
            assert data["type"] == "markdown"
            assert "User Guide" in data["content"]

    def test_get_content_example_file_success(self, client, mock_project_root):
        """Test successful example file content retrieval."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/content?file_path=examples/example1.py")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "example1.py"
            assert data["path"] == "examples/example1.py"
            assert data["type"] == "python"
            assert "Example 1" in data["content"]

    def test_get_content_file_not_found(self, client, mock_project_root):
        """Test content retrieval for non-existent file."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/content?file_path=docs/nonexistent.md")

            assert response.status_code == 404
            assert "File not found" in response.json()["detail"]

    def test_get_content_invalid_prefix(self, client, mock_project_root):
        """Test content retrieval with invalid path prefix."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/content?file_path=config/secrets.txt")

            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]

    def test_get_content_directory_traversal_attempt(self, client, mock_project_root):
        """Test security against directory traversal attack."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/content?file_path=docs/../../etc/passwd")

            assert response.status_code == 403
            # Either "Access denied" or "Invalid path" is acceptable for security
            detail = response.json()["detail"]
            assert "Access denied" in detail or "Invalid path" in detail

    def test_get_content_not_a_file(self, client, mock_project_root):
        """Test content retrieval for directory instead of file."""
        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root):
            response = client.get("/api/v1/devdocs/content?file_path=docs/")

            assert response.status_code in [400, 404]  # Either "Not a file" or "File not found"

    def test_get_content_read_error(self, client, mock_project_root):
        """Test content retrieval with read error."""
        # Create a file
        bad_file = mock_project_root / "docs" / "bad.md"
        bad_file.write_text("content")

        with patch("app.routers.devdocs.get_project_root", return_value=mock_project_root), patch.object(
            Path, "read_text", side_effect=IOError("Permission denied")
        ):
            response = client.get("/api/v1/devdocs/content?file_path=docs/bad.md")

            assert response.status_code == 500
            assert "Error reading file" in response.json()["detail"]


class TestDevDocsHelperFunctions:
    """Test helper functions in devdocs router."""

    def test_get_file_type_markdown(self):
        """Test file type detection for markdown."""
        from app.routers.devdocs import get_file_type

        assert get_file_type("README.md") == "markdown"
        assert get_file_type("guide.MD") == "markdown"

    def test_get_file_type_python(self):
        """Test file type detection for Python."""
        from app.routers.devdocs import get_file_type

        assert get_file_type("example.py") == "python"
        assert get_file_type("script.PY") == "python"

    def test_get_file_type_text(self):
        """Test file type detection for other files."""
        from app.routers.devdocs import get_file_type

        assert get_file_type("notes.txt") == "text"
        assert get_file_type("data.json") == "text"
        assert get_file_type("config.yaml") == "text"

    def test_get_project_root(self):
        """Test project root detection."""
        from app.routers.devdocs import get_project_root

        root = get_project_root()
        assert root.exists()
        assert root.is_dir()
        # Should be 3 levels up from app/routers/devdocs.py
        assert (root / "app" / "routers" / "devdocs.py").exists()

