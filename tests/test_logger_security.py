"""
Tests for logger security module.

Tests sensitive data sanitization and masking functionality.
"""

import constants
from logger.security import (
    _is_sensitive_field,
    _mask_value,
    mask_api_key,
    sanitize_log_data,
)


class TestSanitizeLogData:
    """Test suite for sanitize_log_data function."""

    def test_sanitize_api_key(self):
        """Test API key sanitization."""
        data = {"user": "john", "api_key": "sk-1234567890abcdef"}
        result = sanitize_log_data(data)

        assert result["user"] == "john"
        assert result["api_key"] == "****...cdef"

    def test_sanitize_password(self):
        """Test password sanitization."""
        data = {"username": "admin", "password": "secretpassword123"}
        result = sanitize_log_data(data)

        assert result["username"] == "admin"
        assert result["password"] == "****...d123"

    def test_sanitize_token(self):
        """Test token sanitization."""
        data = {"user_id": "123", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        result = sanitize_log_data(data)

        assert result["user_id"] == "123"
        assert result["token"] == "****...VCJ9"

    def test_sanitize_multiple_sensitive_fields(self):
        """Test sanitization of multiple sensitive fields."""
        data = {
            "user": "john",
            "api_key": "sk-1234567890",
            "password": "mypassword",
            "access_token": "token123456",
        }
        result = sanitize_log_data(data)

        assert result["user"] == "john"
        assert result["api_key"] == "****...7890"
        assert result["password"] == "****...word"
        assert result["access_token"] == "****...3456"

    def test_sanitize_nested_dict_with_nonsensitive_parent(self):
        """Test sanitization of nested dictionaries with non-sensitive parent key."""
        data = {
            "user": "john",
            "metadata": {"api_key": "sk-1234567890", "password": "secret123"},
        }
        result = sanitize_log_data(data)

        assert result["user"] == "john"
        assert isinstance(result["metadata"], dict)
        assert result["metadata"]["api_key"] == "****...7890"
        assert result["metadata"]["password"] == "****...t123"

    def test_sanitize_non_dict_returns_unchanged(self):
        """Test that non-dict input returns unchanged."""
        data = "not a dict"
        result = sanitize_log_data(data)

        assert result == "not a dict"

    def test_sanitize_empty_dict(self):
        """Test sanitization of empty dictionary."""
        data = {}
        result = sanitize_log_data(data)

        assert result == {}

    def test_sanitize_preserves_non_sensitive_fields(self):
        """Test that non-sensitive fields are preserved."""
        data = {
            "user_id": "12345",
            "email": "user@example.com",
            "timestamp": "2025-01-28T10:00:00Z",
            "api_key": "sk-sensitive",
        }
        result = sanitize_log_data(data)

        assert result["user_id"] == "12345"
        assert result["email"] == "user@example.com"
        assert result["timestamp"] == "2025-01-28T10:00:00Z"
        assert result["api_key"] == "****...tive"


class TestIsSensitiveField:
    """Test suite for _is_sensitive_field function."""

    def test_api_key_is_sensitive(self):
        """Test that api_key is detected as sensitive."""
        assert _is_sensitive_field("api_key") is True
        assert _is_sensitive_field("API_KEY") is True
        assert _is_sensitive_field("my_api_key") is True

    def test_password_is_sensitive(self):
        """Test that password is detected as sensitive."""
        assert _is_sensitive_field("password") is True
        assert _is_sensitive_field("PASSWORD") is True
        assert _is_sensitive_field("user_password") is True

    def test_token_is_sensitive(self):
        """Test that token fields are detected as sensitive."""
        assert _is_sensitive_field("token") is True
        assert _is_sensitive_field("access_token") is True
        assert _is_sensitive_field("refresh_token") is True

    def test_secret_is_sensitive(self):
        """Test that secret fields are detected as sensitive."""
        assert _is_sensitive_field("secret") is True
        assert _is_sensitive_field("client_secret") is True
        assert _is_sensitive_field("SECRET_KEY") is True

    def test_auth_is_sensitive(self):
        """Test that auth fields are detected as sensitive."""
        assert _is_sensitive_field("auth") is True
        assert _is_sensitive_field("authorization") is True

    def test_normal_field_not_sensitive(self):
        """Test that normal fields are not detected as sensitive."""
        assert _is_sensitive_field("user_id") is False
        assert _is_sensitive_field("email") is False
        assert _is_sensitive_field("name") is False
        assert _is_sensitive_field("timestamp") is False


class TestMaskValue:
    """Test suite for _mask_value function."""

    def test_mask_long_value(self):
        """Test masking of long values."""
        result = _mask_value("sk-1234567890abcdef")
        assert result == "****...cdef"

    def test_mask_shows_last_4_chars(self):
        """Test that mask shows last 4 characters."""
        result = _mask_value("verylongapikey12345678")
        assert result == "****...5678"

    def test_mask_none_value(self):
        """Test masking of None values."""
        result = _mask_value(None)
        assert result == constants.MASK_NONE_VALUE

    def test_mask_short_value(self):
        """Test masking of values shorter than minimum length."""
        result = _mask_value("abc")
        assert result == constants.MASK_PREFIX + constants.MASK_SHORT_VALUE

    def test_mask_exactly_min_length(self):
        """Test masking of value exactly at minimum length."""
        result = _mask_value("12345678")
        assert result == "****...5678"

    def test_mask_converts_to_string(self):
        """Test that non-string values are converted to strings."""
        result = _mask_value(12345678)
        assert result == "****...5678"


class TestMaskApiKey:
    """Test suite for mask_api_key function."""

    def test_mask_openai_key(self):
        """Test masking of OpenAI-style API key."""
        result = mask_api_key("sk-1234567890abcdef")
        assert result == "****...cdef"

    def test_mask_google_key(self):
        """Test masking of Google-style API key."""
        result = mask_api_key("AIzaSyC1234567890abcdefghij")
        assert result == "****...ghij"

    def test_mask_generic_key(self):
        """Test masking of generic API key."""
        result = mask_api_key("myapikey123456789")
        assert result == "****...6789"

    def test_mask_short_key(self):
        """Test masking of short API key."""
        result = mask_api_key("abc")
        assert result == constants.MASK_PREFIX + constants.MASK_SHORT_VALUE

    def test_mask_empty_key(self):
        """Test masking of empty string."""
        result = mask_api_key("")
        assert result == constants.MASK_PREFIX + constants.MASK_SHORT_VALUE


class TestIntegration:
    """Integration tests for security module."""

    def test_sanitize_complex_log_data(self):
        """Test sanitization of complex nested log data."""
        data = {
            "request_id": "req-123",
            "user": {
                "id": "user-456",
                "email": "user@example.com",
                "api_key": "sk-verylongapikey123",
            },
            "session_info": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "refresh_token": "refresh123456789",
                "expires_at": "2025-12-31T23:59:59Z",
            },
            "metadata": {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"},
        }

        result = sanitize_log_data(data)

        # Non-sensitive fields preserved
        assert result["request_id"] == "req-123"
        assert result["user"]["id"] == "user-456"
        assert result["user"]["email"] == "user@example.com"
        assert result["session_info"]["expires_at"] == "2025-12-31T23:59:59Z"
        assert result["metadata"]["ip_address"] == "192.168.1.1"
        assert result["metadata"]["user_agent"] == "Mozilla/5.0"

        # Sensitive fields masked
        assert result["user"]["api_key"] == "****...y123"
        assert result["session_info"]["token"] == "****...VCJ9"
        assert result["session_info"]["refresh_token"] == "****...6789"

    def test_sanitize_common_sensitive_field_types(self):
        """Test that common sensitive field types are masked."""
        data = {
            "api_key": "key1234567890",
            "password": "pass1234567890",
            "token": "token1234567890",
            "access_token": "token2234567890",
            "secret": "secret1234567890",
            "client_secret": "secret2234567890",
            "credential": "credential1234567890",
        }

        result = sanitize_log_data(data)

        # All should be masked with correct format
        assert result["api_key"] == "****...7890"
        assert result["password"] == "****...7890"
        assert result["token"] == "****...7890"
        assert result["access_token"] == "****...7890"
        assert result["secret"] == "****...7890"
        assert result["client_secret"] == "****...7890"
        assert result["credential"] == "****...7890"
