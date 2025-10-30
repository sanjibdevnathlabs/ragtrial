"""
UI configuration classes.

Contains configuration for Streamlit UI settings.
"""


class UIConfig:
    """UI (Streamlit) configuration"""

    enabled: bool = True
    host: str = "localhost"
    port: int = 8501
    headless: bool = True
    enable_cors: bool = False
    enable_xsrf_protection: bool = False
    startup_timeout: int = 10  # seconds to wait for Streamlit to start
    shutdown_timeout: int = 5  # seconds to wait for graceful shutdown
