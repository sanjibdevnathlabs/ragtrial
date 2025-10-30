"""
Health check service.

Provides system health status information with component-level checks.
"""

import time
from typing import Dict, Optional, Tuple

import constants
import trace.codes as codes
from app.modules.health.response import ComponentHealth, HealthResponse
from config import Config
from database.session import SessionFactory
from embeddings.factory import create_embeddings
from logger import get_logger
from utils.singleton import SingletonMeta
from vectorstore.factory import create_vectorstore

logger = get_logger(__name__)

API_VERSION = "1.0.0"


class HealthService(metaclass=SingletonMeta):
    """
    Singleton service for health check operations.

    Thread-safe singleton ensures only one instance exists.
    Performs fast health checks for critical components (database, vectorstore)
    and cached health checks for expensive external dependencies (LLM, Embeddings).
    """

    def __init__(self, config: Config):
        """
        Initialize health service.

        Only called once - subsequent calls return existing instance.

        Args:
            config: Application configuration
        """
        # Only initialize once
        if not hasattr(self, "_initialized"):
            self.config = config

            # Cache for external dependency health (with timestamp)
            # Format: (is_healthy, timestamp)
            self._llm_health_cache: Optional[Tuple[bool, float]] = None
            self._embeddings_health_cache: Optional[Tuple[bool, float]] = None

            self._initialized = True

    def get_health_status(self) -> HealthResponse:
        """
        Get comprehensive system health status.

        Checks:
        - Database (uncached, fast)
        - Vectorstore (uncached, fast)
        - LLM API (cached, expensive)
        - Embeddings API (cached, expensive)

        Returns:
            HealthResponse: Service health information with component details
        """
        logger.info(codes.API_HEALTH_CHECK_STARTED)
        start_time = time.time()

        components = []

        # Critical components - NO CACHING
        db_healthy, db_details = self._check_database_health()
        components.append(
            ComponentHealth(
                name=constants.COMPONENT_DATABASE,
                status=(
                    constants.HEALTH_STATUS_HEALTHY
                    if db_healthy
                    else constants.HEALTH_STATUS_UNHEALTHY
                ),
                category=constants.COMPONENT_CATEGORY_CRITICAL,
                details=db_details,
            )
        )

        vs_healthy, vs_details = self._check_vectorstore_health()
        components.append(
            ComponentHealth(
                name=constants.COMPONENT_VECTORSTORE,
                status=(
                    constants.HEALTH_STATUS_HEALTHY
                    if vs_healthy
                    else constants.HEALTH_STATUS_UNHEALTHY
                ),
                category=constants.COMPONENT_CATEGORY_CRITICAL,
                details=vs_details,
            )
        )

        # External dependencies - CACHED (expensive)
        llm_healthy, llm_details = self._check_llm_health_cached()
        components.append(
            ComponentHealth(
                name=constants.COMPONENT_LLM,
                status=(
                    constants.HEALTH_STATUS_HEALTHY
                    if llm_healthy
                    else constants.HEALTH_STATUS_UNHEALTHY
                ),
                category=constants.COMPONENT_CATEGORY_DEPENDENCY,
                details=llm_details,
            )
        )

        emb_healthy, emb_details = self._check_embeddings_health_cached()
        components.append(
            ComponentHealth(
                name=constants.COMPONENT_EMBEDDINGS,
                status=(
                    constants.HEALTH_STATUS_HEALTHY
                    if emb_healthy
                    else constants.HEALTH_STATUS_UNHEALTHY
                ),
                category=constants.COMPONENT_CATEGORY_DEPENDENCY,
                details=emb_details,
            )
        )

        # Overall status: unhealthy if ANY critical component fails
        overall_healthy = db_healthy and vs_healthy

        elapsed = (time.time() - start_time) * 1000  # ms
        logger.info(
            codes.API_HEALTH_CHECK_COMPLETED,
            status=(
                constants.HEALTH_STATUS_HEALTHY
                if overall_healthy
                else constants.HEALTH_STATUS_UNHEALTHY
            ),
            duration_ms=f"{elapsed:.2f}",
            database=db_healthy,
            vectorstore=vs_healthy,
            llm=llm_healthy,
            embeddings=emb_healthy,
        )

        return HealthResponse(
            status=(
                constants.HEALTH_STATUS_HEALTHY
                if overall_healthy
                else constants.HEALTH_STATUS_UNHEALTHY
            ),
            version=API_VERSION,
            components=components,
        )

    def _check_database_health(self) -> Tuple[bool, Dict[str, str]]:
        """
        Check database health (uncached, fast).

        Returns:
            Tuple of (is_healthy, details_dict)
        """
        logger.debug(codes.HEALTH_CHECK_DATABASE_CHECKING)

        try:
            session_factory = SessionFactory()
            is_healthy = session_factory.check_health()

            details = {
                "type": self.config.database.driver,
            }

            if is_healthy:
                logger.debug(codes.HEALTH_CHECK_DATABASE_HEALTHY)
            else:
                logger.error(codes.HEALTH_CHECK_DATABASE_UNHEALTHY)

            return is_healthy, details

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_DATABASE_UNHEALTHY, error=str(e), exc_info=True
            )
            return False, {"type": self.config.database.driver, "error": str(e)}

    def _check_vectorstore_health(self) -> Tuple[bool, Dict[str, str]]:
        """
        Check vectorstore health (uncached, fast).

        Returns:
            Tuple of (is_healthy, details_dict)
        """
        logger.debug(codes.HEALTH_CHECK_VECTORSTORE_CHECKING)

        try:
            # Create embeddings and vectorstore
            embeddings = create_embeddings(self.config)
            vectorstore = create_vectorstore(self.config, embeddings)

            # Initialize if needed (should be fast if already initialized)
            if not hasattr(vectorstore, "collection") or vectorstore.collection is None:
                vectorstore.initialize()

            is_healthy = vectorstore.check_health()

            details = {
                "provider": self.config.vectorstore.provider,
            }

            if is_healthy:
                logger.debug(codes.HEALTH_CHECK_VECTORSTORE_HEALTHY)
            else:
                logger.error(codes.HEALTH_CHECK_VECTORSTORE_UNHEALTHY)

            return is_healthy, details

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_VECTORSTORE_UNHEALTHY, error=str(e), exc_info=True
            )
            return False, {
                "provider": self.config.vectorstore.provider,
                "error": str(e),
            }

    def _check_llm_health_cached(self) -> Tuple[bool, Dict[str, str]]:
        """
        Check LLM API health with caching (expensive API call).

        Makes a minimal API call to verify LLM availability.
        Uses a tiny prompt to minimize token usage and cost.

        Returns:
            Tuple of (is_healthy, details_dict)
        """
        current_time = time.time()

        # Check cache
        if self._llm_health_cache is not None:
            cached_status, cached_time = self._llm_health_cache
            age = current_time - cached_time

            if age < constants.HEALTH_CHECK_CACHE_DURATION:
                return cached_status, {
                    "provider": self.config.rag.provider,
                    "cached": "true",
                    "cache_age_seconds": f"{age:.1f}",
                }

        # Perform actual check
        logger.debug(codes.HEALTH_CHECK_LLM_CHECKING, provider=self.config.rag.provider)

        try:
            is_healthy = self._test_llm_api()

            # Cache the result
            self._llm_health_cache = (is_healthy, current_time)

            return is_healthy, {"provider": self.config.rag.provider, "cached": "false"}

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_LLM_UNHEALTHY,
                provider=self.config.rag.provider,
                error=str(e),
                exc_info=True,
            )
            # Cache failure too
            self._llm_health_cache = (False, current_time)
            return False, {"provider": self.config.rag.provider, "error": str(e)}

    def _check_embeddings_health_cached(self) -> Tuple[bool, Dict[str, str]]:
        """
        Check Embeddings API health with caching (expensive API call).

        Generates a minimal test embedding to verify API availability.
        Uses tiny text to minimize token usage and cost.

        Returns:
            Tuple of (is_healthy, details_dict)
        """
        current_time = time.time()

        # Check cache
        if self._embeddings_health_cache is not None:
            cached_status, cached_time = self._embeddings_health_cache
            age = current_time - cached_time

            if age < constants.HEALTH_CHECK_CACHE_DURATION:
                return cached_status, {
                    "provider": self.config.embeddings.provider,
                    "cached": "true",
                    "cache_age_seconds": f"{age:.1f}",
                }

        # Perform actual check
        logger.debug(
            codes.HEALTH_CHECK_EMBEDDINGS_CHECKING,
            provider=self.config.embeddings.provider,
        )

        try:
            is_healthy = self._test_embeddings_api()

            # Cache the result
            self._embeddings_health_cache = (is_healthy, current_time)

            return is_healthy, {
                "provider": self.config.embeddings.provider,
                "cached": "false",
            }

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_EMBEDDINGS_UNHEALTHY,
                provider=self.config.embeddings.provider,
                error=str(e),
                exc_info=True,
            )
            # Cache failure too
            self._embeddings_health_cache = (False, current_time)
            return False, {"provider": self.config.embeddings.provider, "error": str(e)}

    def _test_llm_api(self) -> bool:
        """
        Test LLM API with minimal prompt.

        Uses the LLM factory to create the correct instance,
        then makes a minimal API call to verify availability.

        Returns:
            True if LLM responds successfully, False otherwise
        """
        try:
            from llm.factory import create_llm

            # Create LLM with deterministic settings for health check
            # NOTE: Do NOT override max_tokens or max_output_tokens for Google Gemini
            # as it causes empty responses. Use config defaults instead.
            llm = create_llm(
                self.config,
                temperature=0,  # Deterministic responses
            )

            # Minimal prompt for health check
            response = llm.invoke("Hi")
            return response is not None and len(str(response.content)) > 0

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_LLM_UNHEALTHY,
                provider=self.config.rag.provider,
                error=str(e),
                exc_info=True,
            )
            return False

    def _test_embeddings_api(self) -> bool:
        """
        Test Embeddings API with minimal text.

        Makes an actual API call to verify embeddings availability.
        Uses minimal text to reduce cost.

        Returns:
            True if embeddings responds successfully, False otherwise
        """
        try:
            from embeddings.factory import create_embeddings

            embeddings = create_embeddings(self.config)

            # Minimal text - generates single embedding vector
            test_text = "hi"
            result = embeddings.embed_query(test_text)

            # Verify we got a valid embedding vector
            return result is not None and len(result) > 0

        except Exception as e:
            logger.error(
                codes.HEALTH_CHECK_EMBEDDINGS_UNHEALTHY,
                provider=self.config.embeddings.provider,
                error=str(e),
                exc_info=True,
            )
            return False
