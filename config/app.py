"""
Application configuration classes.

Contains configuration for application metadata.
"""


class AppConfig:
    """Holds application metadata from the [app] TOML section"""
    name: str = None
    environment: str = None
    version: str = None

