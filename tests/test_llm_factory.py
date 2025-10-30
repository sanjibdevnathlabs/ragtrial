"""
Unit tests for LLM factory.

Tests the factory pattern for creating LLM instances across different providers.
All external dependencies (LangChain) are mocked.
"""

import pytest
from unittest.mock import MagicMock, patch

import constants
from config import Config
from llm.factory import create_llm


@pytest.fixture
def config_google():
    """Config with Google provider."""
    return Config()  # Uses test.toml with Google as default


@pytest.fixture
def config_openai(monkeypatch):
    """Config with OpenAI provider."""
    monkeypatch.setenv("APP_ENV", "test")
    config = Config()
    config.rag.provider = constants.LLM_PROVIDER_OPENAI
    return config


@pytest.fixture
def config_anthropic(monkeypatch):
    """Config with Anthropic provider."""
    monkeypatch.setenv("APP_ENV", "test")
    config = Config()
    config.rag.provider = constants.LLM_PROVIDER_ANTHROPIC
    return config


class TestCreateLLMGoogle:
    """Test LLM factory with Google Gemini provider."""

    def test_create_google_llm_success(self, config_google):
        """Test creating Google LLM with default config."""
        with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_google)

            assert llm is not None
            assert llm == mock_instance
            mock_llm.assert_called_once()

            # Verify initialization parameters
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["model"] == config_google.rag.google.model
            assert call_kwargs["temperature"] == config_google.rag.google.temperature
            assert (
                call_kwargs["max_output_tokens"] == config_google.rag.google.max_tokens
            )

    def test_create_google_llm_with_overrides(self, config_google):
        """Test creating Google LLM with parameter overrides."""
        with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_google, temperature=0, max_output_tokens=10)

            assert llm is not None
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["temperature"] == 0
            assert call_kwargs["max_output_tokens"] == 10

    def test_create_google_llm_with_api_key(self, config_google):
        """Test creating Google LLM with API key."""
        config_google.rag.google.api_key = "test-google-key"

        with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_google)

            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["google_api_key"] == "test-google-key"

    def test_google_llm_invoke_method_exists(self, config_google):
        """Test that created LLM has invoke method (duck typing)."""
        with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(content="Test response")
            mock_llm.return_value = mock_instance

            llm = create_llm(config_google)

            assert hasattr(llm, "invoke")
            assert callable(llm.invoke)

            # Test invoke
            response = llm.invoke("Test prompt")
            assert response.content == "Test response"


class TestCreateLLMOpenAI:
    """Test LLM factory with OpenAI GPT provider."""

    def test_create_openai_llm_success(self, config_openai):
        """Test creating OpenAI LLM with default config."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_openai)

            assert llm is not None
            assert llm == mock_instance
            mock_llm.assert_called_once()

            # Verify initialization parameters
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["model"] == config_openai.rag.openai.model
            assert call_kwargs["temperature"] == config_openai.rag.openai.temperature
            assert call_kwargs["max_tokens"] == config_openai.rag.openai.max_tokens

    def test_create_openai_llm_with_overrides(self, config_openai):
        """Test creating OpenAI LLM with parameter overrides."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_openai, temperature=0, max_tokens=10)

            assert llm is not None
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["temperature"] == 0
            assert call_kwargs["max_tokens"] == 10

    def test_create_openai_llm_with_api_key(self, config_openai):
        """Test creating OpenAI LLM with API key."""
        config_openai.rag.openai.api_key = "test-openai-key"

        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_openai)

            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["api_key"] == "test-openai-key"

    def test_openai_llm_invoke_method_exists(self, config_openai):
        """Test that created LLM has invoke method (duck typing)."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(content="Test response")
            mock_llm.return_value = mock_instance

            llm = create_llm(config_openai)

            assert hasattr(llm, "invoke")
            assert callable(llm.invoke)

            # Test invoke
            response = llm.invoke("Test prompt")
            assert response.content == "Test response"


class TestCreateLLMAnthropic:
    """Test LLM factory with Anthropic Claude provider."""

    def test_create_anthropic_llm_success(self, config_anthropic):
        """Test creating Anthropic LLM with default config."""
        with patch("langchain_anthropic.ChatAnthropic") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_anthropic)

            assert llm is not None
            assert llm == mock_instance
            mock_llm.assert_called_once()

            # Verify initialization parameters
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["model"] == config_anthropic.rag.anthropic.model
            assert (
                call_kwargs["temperature"] == config_anthropic.rag.anthropic.temperature
            )
            assert (
                call_kwargs["max_tokens"] == config_anthropic.rag.anthropic.max_tokens
            )

    def test_create_anthropic_llm_with_overrides(self, config_anthropic):
        """Test creating Anthropic LLM with parameter overrides."""
        with patch("langchain_anthropic.ChatAnthropic") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_anthropic, temperature=0, max_tokens=10)

            assert llm is not None
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["temperature"] == 0
            assert call_kwargs["max_tokens"] == 10

    def test_create_anthropic_llm_with_api_key(self, config_anthropic):
        """Test creating Anthropic LLM with API key."""
        config_anthropic.rag.anthropic.api_key = "test-anthropic-key"

        with patch("langchain_anthropic.ChatAnthropic") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = create_llm(config_anthropic)

            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs["anthropic_api_key"] == "test-anthropic-key"

    def test_anthropic_llm_invoke_method_exists(self, config_anthropic):
        """Test that created LLM has invoke method (duck typing)."""
        with patch("langchain_anthropic.ChatAnthropic") as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(content="Test response")
            mock_llm.return_value = mock_instance

            llm = create_llm(config_anthropic)

            assert hasattr(llm, "invoke")
            assert callable(llm.invoke)

            # Test invoke
            response = llm.invoke("Test prompt")
            assert response.content == "Test response"


class TestFactoryErrorHandling:
    """Test LLM factory error handling."""

    def test_unsupported_provider_raises_error(self, config_google):
        """Test that unsupported provider raises ValueError."""
        config_google.rag.provider = "unsupported_provider"

        with pytest.raises(ValueError) as exc_info:
            create_llm(config_google)

        assert "Unsupported LLM provider" in str(exc_info.value)
        assert "unsupported_provider" in str(exc_info.value)

    def test_empty_provider_raises_error(self, config_google):
        """Test that empty provider raises ValueError."""
        config_google.rag.provider = ""

        with pytest.raises(ValueError) as exc_info:
            create_llm(config_google)

        assert "Unsupported LLM provider" in str(exc_info.value)


class TestProviderSwitching:
    """Test switching between providers."""

    def test_switch_from_google_to_openai(self, config_google):
        """Test switching provider from Google to OpenAI."""
        # Create Google LLM
        with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_google:
            mock_google.return_value = MagicMock()
            llm_google = create_llm(config_google)
            assert llm_google is not None

        # Switch to OpenAI
        config_google.rag.provider = constants.LLM_PROVIDER_OPENAI
        with patch("langchain_openai.ChatOpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            llm_openai = create_llm(config_google)
            assert llm_openai is not None
            assert llm_openai != llm_google

    def test_multiple_providers_in_sequence(self, config_google):
        """Test creating multiple providers sequentially."""
        providers = [
            (
                constants.LLM_PROVIDER_GOOGLE,
                "langchain_google_genai.ChatGoogleGenerativeAI",
            ),
            (constants.LLM_PROVIDER_OPENAI, "langchain_openai.ChatOpenAI"),
            (constants.LLM_PROVIDER_ANTHROPIC, "langchain_anthropic.ChatAnthropic"),
        ]

        llms = []
        for provider, patch_path in providers:
            config_google.rag.provider = provider
            with patch(patch_path) as mock_llm:
                mock_instance = MagicMock()
                mock_llm.return_value = mock_instance
                llm = create_llm(config_google)
                llms.append(llm)

        # Verify all LLMs were created
        assert len(llms) == 3
        assert all(llm is not None for llm in llms)


class TestLLMProtocolCompliance:
    """Test that created LLMs comply with LLMProtocol."""

    def test_google_llm_protocol_compliance(self, config_google):
        """Test Google LLM follows LLMProtocol."""
        with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke = MagicMock(return_value=MagicMock(content="response"))
            mock_llm.return_value = mock_instance

            llm = create_llm(config_google)

            # Check protocol methods exist
            assert hasattr(llm, "invoke")
            assert callable(llm.invoke)

    def test_openai_llm_protocol_compliance(self, config_openai):
        """Test OpenAI LLM follows LLMProtocol."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke = MagicMock(return_value=MagicMock(content="response"))
            mock_llm.return_value = mock_instance

            llm = create_llm(config_openai)

            # Check protocol methods exist
            assert hasattr(llm, "invoke")
            assert callable(llm.invoke)

    def test_anthropic_llm_protocol_compliance(self, config_anthropic):
        """Test Anthropic LLM follows LLMProtocol."""
        with patch("langchain_anthropic.ChatAnthropic") as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke = MagicMock(return_value=MagicMock(content="response"))
            mock_llm.return_value = mock_instance

            llm = create_llm(config_anthropic)

            # Check protocol methods exist
            assert hasattr(llm, "invoke")
            assert callable(llm.invoke)
