"""
Trace codes and messages package.

This package contains all trace codes (event names) and messages used
throughout the application. NO string literals should be used in the code.

All constants use UPPER_SNAKE_CASE naming convention.

Usage:
    from trace import codes
    
    logger.info(codes.INGESTION_SCRIPT_STARTED)
    logger.error(codes.GEMINI_API_KEY_MISSING, 
                 message=codes.MSG_GEMINI_API_KEY_MISSING)
    
    logger.info(codes.CONFIG_LOADED, message=codes.MSG_CONFIG_LOADED)
"""

# Import codes module for dotted notation access
from trace import codes

__all__ = ["codes"]
