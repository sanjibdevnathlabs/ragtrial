"""
Tests for health check service.

Tests health status endpoint functionality.
"""

import pytest
from unittest.mock import Mock

from app.modules.health import HealthService
from app.modules.health.response import HealthResponse
from config import Config


@pytest.fixture
def mock_config():
    """Mock configuration."""
    config = Mock()
    config.storage = Mock()
    config.storage.backend = "local"
    return config


class TestHealthService:
    """Test suite for HealthService."""
    
    def test_get_health_status_returns_response(self, mock_config):
        """Test health status returns HealthResponse."""
        service = HealthService(mock_config)
        
        result = service.get_health_status()
        
        assert isinstance(result, HealthResponse)
    
    def test_get_health_status_has_correct_status(self, mock_config):
        """Test health status returns healthy."""
        service = HealthService(mock_config)
        
        result = service.get_health_status()
        
        assert result.status == "healthy"
    
    def test_get_health_status_includes_storage_backend(self, mock_config):
        """Test health status includes storage backend."""
        service = HealthService(mock_config)
        
        result = service.get_health_status()
        
        assert result.storage_backend == "local"
    
    def test_get_health_status_includes_version(self, mock_config):
        """Test health status includes API version."""
        service = HealthService(mock_config)
        
        result = service.get_health_status()
        
        assert result.version is not None
        assert len(result.version) > 0
    
    def test_get_health_status_with_s3_backend(self, mock_config):
        """Test health status with S3 backend."""
        mock_config.storage.backend = "s3"
        service = HealthService(mock_config)
        
        result = service.get_health_status()
        
        assert result.storage_backend == "s3"

