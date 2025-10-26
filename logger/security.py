"""
Security utilities for logging.

Provides functions to sanitize sensitive data before logging to prevent
accidental exposure of API keys, tokens, passwords, and other secrets.
"""

from typing import Any, Dict
from constants import (
    SENSITIVE_FIELDS,
    MASK_PREFIX,
    MASK_SUFFIX_LENGTH,
    MASK_MIN_LENGTH,
    MASK_NONE_VALUE,
    MASK_SHORT_VALUE
)


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive data in log dictionary.
    
    Masks values for sensitive fields (api_key, password, token, etc.)
    using the pattern: ****...last4chars
    
    Args:
        data: Dictionary of log data that may contain sensitive information
        
    Returns:
        Dictionary with sensitive values masked
        
    Example:
        data = {"user": "john", "api_key": "sk-1234567890abcdef"}
        sanitized = sanitize_log_data(data)
        # Returns: {"user": "john", "api_key": "****...cdef"}
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if _is_sensitive_field(key):
            sanitized[key] = _mask_value(value)
            continue
        
        if isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
            continue
        
        sanitized[key] = value
    
    return sanitized


def _is_sensitive_field(field_name: str) -> bool:
    """
    Check if a field name indicates sensitive data.
    
    Args:
        field_name: Name of the field to check
        
    Returns:
        True if field is sensitive, False otherwise
    """
    field_lower = field_name.lower()
    return any(sensitive in field_lower for sensitive in SENSITIVE_FIELDS)


def _mask_value(value: Any) -> str:
    """
    Mask a sensitive value.
    
    Args:
        value: Value to mask
        
    Returns:
        Masked string in format: ****...last4
    """
    if value is None:
        return MASK_NONE_VALUE
    
    value_str = str(value)
    
    if len(value_str) < MASK_MIN_LENGTH:
        return MASK_PREFIX + MASK_SHORT_VALUE
    
    suffix = value_str[-MASK_SUFFIX_LENGTH:]
    return f"{MASK_PREFIX}{suffix}"


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key for safe logging.
    
    Args:
        api_key: API key to mask
        
    Returns:
        Masked API key
        
    Example:
        masked = mask_api_key("sk-1234567890abcdef")
        # Returns: "****...cdef"
    """
    return _mask_value(api_key)

