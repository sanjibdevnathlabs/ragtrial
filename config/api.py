"""
API server configuration classes.

Contains configuration for FastAPI server settings.
"""


class APIConfig:
    """API server configuration"""

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = None
    upload_chunk_size: int = 1048576  # 1MB
