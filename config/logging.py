"""
Logging configuration classes.

Contains configuration for structured logging setup.
"""


class LoggingConfig:
    """Holds logging configuration from the [logging] TOML section"""

    level: str = "INFO"
    format: str = "console"
    include_caller: bool = False
    include_process_info: bool = False
