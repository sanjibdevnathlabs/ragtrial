"""
Integration tests for query API endpoints.

Tests the query router with FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.api.main import app
from app.modules.query.service import QueryService
import constants


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_query_service():
    """Create a mock query service."""
    mock = Mock(spec=QueryService)
    mock.query.return_value = {
        constants.RESPONSE_KEY_ANSWER: "Test answer from RAG",
        constants.RESPONSE_KEY_SOURCES: [
            {
                "metadata": {
                    constants.META_SOURCE: "source_docs/test.pdf"
                },
                "content": "Test content"
            }
        ],
        constants.RESPONSE_KEY_HAS_ANSWER: True,
        constants.RESPONSE_KEY_QUERY: "What is RAG?"
    }
    mock.health_check.return_value = {
        "rag_initialized": True,
        "provider": "google",
        "model": "gemini-pro"
    }
    return mock


class TestQueryEndpoint:
    """Test POST /query endpoint."""
    
    @patch('app.routers.query.QueryService')
    def test_query_success(self, mock_service_class, client, mock_query_service):
        """Test successful query request."""
        mock_service_class.return_value = mock_query_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "What is RAG?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert constants.RESPONSE_KEY_ANSWER in data
        assert constants.RESPONSE_KEY_SOURCES in data
        assert constants.RESPONSE_KEY_HAS_ANSWER in data
        assert data[constants.RESPONSE_KEY_QUERY] == "What is RAG?"
        
        mock_query_service.query.assert_called_once_with("What is RAG?")
    
    def test_query_with_empty_question(self, client):
        """Test query with empty question."""
        response = client.post(
            "/api/v1/query",
            json={"question": ""}
        )
        
        assert response.status_code == 422
    
    def test_query_with_whitespace_only(self, client):
        """Test query with whitespace-only question."""
        response = client.post(
            "/api/v1/query",
            json={"question": "   "}
        )
        
        assert response.status_code == 422
    
    def test_query_too_short(self, client):
        """Test query with question below minimum length."""
        response = client.post(
            "/api/v1/query",
            json={"question": "ab"}
        )
        
        assert response.status_code == 422
    
    def test_query_too_long(self, client):
        """Test query with question exceeding maximum length."""
        long_question = "a" * (constants.MAX_QUERY_LENGTH_API + 1)
        response = client.post(
            "/api/v1/query",
            json={"question": long_question}
        )
        
        assert response.status_code == 422
    
    def test_query_at_minimum_length(self, client):
        """Test query at exactly minimum length."""
        question = "a" * constants.MIN_QUERY_LENGTH
        
        with patch('app.routers.query.QueryService') as mock_service_class:
            mock_service = Mock()
            mock_service.query.return_value = {
                constants.RESPONSE_KEY_ANSWER: "Test",
                constants.RESPONSE_KEY_SOURCES: [],
                constants.RESPONSE_KEY_HAS_ANSWER: True,
                constants.RESPONSE_KEY_QUERY: question
            }
            mock_service_class.return_value = mock_service
            
            response = client.post(
                "/api/v1/query",
                json={"question": question}
            )
            
            assert response.status_code == 200
    
    def test_query_missing_question_field(self, client):
        """Test query with missing question field."""
        response = client.post(
            "/api/v1/query",
            json={}
        )
        
        assert response.status_code == 422
    
    @patch('app.routers.query.QueryService')
    def test_query_with_runtime_error(self, mock_service_class, client):
        """Test query when service raises RuntimeError."""
        mock_service = Mock()
        mock_service.query.side_effect = RuntimeError("RAG chain not initialized")
        mock_service_class.return_value = mock_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "What is RAG?"}
        )
        
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
    
    @patch('app.routers.query.QueryService')
    def test_query_with_value_error(self, mock_service_class, client):
        """Test query when service raises ValueError."""
        mock_service = Mock()
        mock_service.query.side_effect = ValueError("Query processing failed")
        mock_service_class.return_value = mock_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "What is RAG?"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
    
    @patch('app.routers.query.QueryService')
    def test_query_with_unexpected_error(self, mock_service_class, client):
        """Test query when service raises unexpected exception."""
        mock_service = Mock()
        mock_service.query.side_effect = Exception("Unexpected error")
        mock_service_class.return_value = mock_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "What is RAG?"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == constants.ERROR_QUERY_PROCESSING_FAILED
    
    @patch('app.routers.query.QueryService')
    def test_query_with_no_answer(self, mock_service_class, client, mock_query_service):
        """Test query when RAG system finds no answer."""
        mock_query_service.query.return_value = {
            constants.RESPONSE_KEY_ANSWER: "I don't have enough information",
            constants.RESPONSE_KEY_SOURCES: [],
            constants.RESPONSE_KEY_HAS_ANSWER: False,
            constants.RESPONSE_KEY_QUERY: "obscure question"
        }
        mock_service_class.return_value = mock_query_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "obscure question"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data[constants.RESPONSE_KEY_HAS_ANSWER] is False
        assert len(data[constants.RESPONSE_KEY_SOURCES]) == 0
    
    @patch('app.routers.query.QueryService')
    def test_query_with_multiple_sources(self, mock_service_class, client, mock_query_service):
        """Test query with multiple source documents."""
        mock_query_service.query.return_value = {
            constants.RESPONSE_KEY_ANSWER: "Answer based on multiple sources",
            constants.RESPONSE_KEY_SOURCES: [
                {
                    "metadata": {constants.META_SOURCE: "source_docs/doc1.pdf"},
                    "content": "Content 1"
                },
                {
                    "metadata": {constants.META_SOURCE: "source_docs/doc2.txt"},
                    "content": "Content 2"
                },
                {
                    "metadata": {constants.META_SOURCE: "source_docs/doc3.md"},
                    "content": "Content 3"
                }
            ],
            constants.RESPONSE_KEY_HAS_ANSWER: True,
            constants.RESPONSE_KEY_QUERY: "test question"
        }
        mock_service_class.return_value = mock_query_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "test question"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data[constants.RESPONSE_KEY_SOURCES]) == 3
        assert data[constants.RESPONSE_KEY_SOURCES][0]["filename"] == "doc1.pdf"
        assert data[constants.RESPONSE_KEY_SOURCES][1]["filename"] == "doc2.txt"
        assert data[constants.RESPONSE_KEY_SOURCES][2]["filename"] == "doc3.md"
    
    @patch('app.routers.query.QueryService')
    def test_query_strips_whitespace(self, mock_service_class, client, mock_query_service):
        """Test that query strips leading/trailing whitespace."""
        mock_service_class.return_value = mock_query_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "  What is RAG?  "}
        )
        
        assert response.status_code == 200
        mock_query_service.query.assert_called_once_with("What is RAG?")


class TestQueryHealthEndpoint:
    """Test GET /query/health endpoint."""
    
    @patch('app.routers.query.QueryService')
    def test_health_check_success(self, mock_service_class, client, mock_query_service):
        """Test successful health check."""
        mock_service_class.return_value = mock_query_service
        
        response = client.get("/api/v1/query/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "rag_system" in data
        assert data["rag_system"]["rag_initialized"] is True
        
        mock_query_service.health_check.assert_called_once()
    
    @patch('app.routers.query.QueryService')
    def test_health_check_when_rag_not_initialized(self, mock_service_class, client):
        """Test health check when RAG chain not yet initialized."""
        mock_service = Mock()
        mock_service.health_check.return_value = {
            "rag_initialized": False,
            "provider": "google",
            "model": "gemini-pro"
        }
        mock_service_class.return_value = mock_service
        
        response = client.get("/api/v1/query/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["rag_system"]["rag_initialized"] is False
    
    @patch('app.routers.query.QueryService')
    def test_health_check_with_service_error(self, mock_service_class, client):
        """Test health check when service raises exception."""
        mock_service = Mock()
        mock_service.health_check.side_effect = Exception("Service error")
        mock_service_class.return_value = mock_service
        
        response = client.get("/api/v1/query/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert "error" in data


class TestResponseFormat:
    """Test response format compliance."""
    
    @patch('app.routers.query.QueryService')
    def test_response_includes_all_required_fields(self, mock_service_class, client, mock_query_service):
        """Test that response includes all required fields."""
        mock_service_class.return_value = mock_query_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "What is RAG?"}
        )
        
        data = response.json()
        
        assert "success" in data
        assert constants.RESPONSE_KEY_ANSWER in data
        assert constants.RESPONSE_KEY_SOURCES in data
        assert constants.RESPONSE_KEY_HAS_ANSWER in data
        assert constants.RESPONSE_KEY_QUERY in data
    
    @patch('app.routers.query.QueryService')
    def test_source_document_format(self, mock_service_class, client, mock_query_service):
        """Test that source documents have correct format."""
        mock_service_class.return_value = mock_query_service
        
        response = client.post(
            "/api/v1/query",
            json={"question": "What is RAG?"}
        )
        
        data = response.json()
        sources = data[constants.RESPONSE_KEY_SOURCES]
        
        if len(sources) > 0:
            source = sources[0]
            assert "filename" in source
            assert "chunk_index" in source
            assert "content" in source

