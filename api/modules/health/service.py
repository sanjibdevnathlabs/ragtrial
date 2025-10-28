"""
Health check service.

Provides system health status information.
"""

from api.models import HealthResponse
from api.utils.singleton import SingletonMeta
from config import Config
from logger import get_logger
import trace.codes as codes

logger = get_logger(__name__)

API_VERSION = "1.0.0"


class HealthService(metaclass=SingletonMeta):
    """
    Singleton service for health check operations.
    
    Thread-safe singleton ensures only one instance exists.
    Optimized for high RPS scenarios.
    """
    
    def __init__(self, config: Config):
        """
        Initialize health service.
        
        Only called once - subsequent calls return existing instance.
        
        Args:
            config: Application configuration
        """
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self.config = config
            self._initialized = True
    
    def get_health_status(self) -> HealthResponse:
        """
        Get system health status.
        
        Returns:
            HealthResponse: Service health information
        """
        logger.debug(codes.API_HEALTH_CHECK_REQUESTED)
        
        return HealthResponse(
            status="healthy",
            storage_backend=self.config.storage.backend,
            version=API_VERSION
        )

