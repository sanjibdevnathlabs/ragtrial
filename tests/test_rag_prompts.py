"""
Tests for RAG prompt templates.

Tests prompt creation and context formatting.
"""

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from app.chain_rag.prompts import (
    RAG_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    create_rag_prompt,
    format_context,
)


class TestCreateRagPrompt:
    """Tests for create_rag_prompt() function."""

    def test_create_rag_prompt_returns_chat_prompt_template(self):
        """Test that create_rag_prompt returns ChatPromptTemplate."""
        prompt = create_rag_prompt()

        assert isinstance(prompt, ChatPromptTemplate)

    def test_create_rag_prompt_contains_system_message(self):
        """Test that prompt contains system message."""
        prompt = create_rag_prompt()

        messages = prompt.messages
        assert len(messages) >= 2
        assert messages[0].prompt.template == SYSTEM_PROMPT

    def test_create_rag_prompt_contains_human_message(self):
        """Test that prompt contains human message."""
        prompt = create_rag_prompt()

        messages = prompt.messages
        assert len(messages) >= 2
        assert messages[1].prompt.template == RAG_PROMPT_TEMPLATE

    def test_create_rag_prompt_has_required_variables(self):
        """Test that prompt has context and question variables."""
        prompt = create_rag_prompt()

        input_variables = prompt.input_variables
        assert "context" in input_variables
        assert "question" in input_variables


class TestFormatContext:
    """Tests for format_context() function."""

    def test_format_context_empty_documents(self):
        """Test formatting with empty document list."""
        result = format_context([])

        assert result == ""

    def test_format_context_single_document(self):
        """Test formatting with single document."""
        docs = [
            Document(
                page_content="This is test content", metadata={"source": "test.txt"}
            )
        ]

        result = format_context(docs)

        # Document references should NOT be present (enhancement)
        assert "[Document" not in result
        assert "Source:" not in result
        # Content should be present
        assert "This is test content" in result
        assert result == "This is test content"

    def test_format_context_multiple_documents(self):
        """Test formatting with multiple documents."""
        docs = [
            Document(page_content="Content 1", metadata={"source": "doc1.txt"}),
            Document(page_content="Content 2", metadata={"source": "doc2.txt"}),
            Document(page_content="Content 3", metadata={"source": "doc3.txt"}),
        ]

        result = format_context(docs)

        # Document references should NOT be present (enhancement)
        assert "[Document" not in result
        assert "Source:" not in result
        # Content should be present
        assert "Content 1" in result
        assert "Content 2" in result
        assert "Content 3" in result
        # Documents separated by separator
        assert "\n\n---\n\n" in result
        assert result == "Content 1\n\n---\n\nContent 2\n\n---\n\nContent 3"

    def test_format_context_document_without_source(self):
        """Test formatting document with missing source metadata."""
        docs = [Document(page_content="Content", metadata={})]

        result = format_context(docs)

        # Document references should NOT be present (enhancement)
        assert "[Document" not in result
        assert "Source:" not in result
        # Content should be present
        assert "Content" in result
        assert result == "Content"

    def test_format_context_strips_whitespace(self):
        """Test that content whitespace is stripped."""
        docs = [
            Document(
                page_content="  Content with whitespace  ",
                metadata={"source": "test.txt"},
            )
        ]

        result = format_context(docs)

        assert "Content with whitespace" in result
        assert "  Content with whitespace  " not in result

    def test_format_context_separates_documents(self):
        """Test that documents are separated properly."""
        docs = [
            Document(page_content="First", metadata={"source": "1.txt"}),
            Document(page_content="Second", metadata={"source": "2.txt"}),
        ]

        result = format_context(docs)

        # Should have double newline between documents
        assert "\n\n" in result

    def test_format_context_with_multiline_content(self):
        """Test formatting with multiline document content."""
        docs = [
            Document(
                page_content="Line 1\nLine 2\nLine 3", metadata={"source": "test.txt"}
            )
        ]

        result = format_context(docs)

        assert "Line 1\nLine 2\nLine 3" in result

    def test_format_context_hides_source_path(self):
        """Test that source paths are NOT exposed in context (enhancement)."""
        docs = [
            Document(
                page_content="Content", metadata={"source": "/path/to/document.pdf"}
            )
        ]

        result = format_context(docs)

        # Document references should NOT be present (enhancement)
        assert "[Document" not in result
        assert "Source:" not in result
        assert "/path/to/document.pdf" not in result
        # Only content should be present
        assert result == "Content"


class TestPromptConstants:
    """Tests for prompt constant strings."""

    def test_system_prompt_not_empty(self):
        """Test that SYSTEM_PROMPT is not empty."""
        assert SYSTEM_PROMPT
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_key_instructions(self):
        """Test that SYSTEM_PROMPT contains key instructions."""
        assert "context" in SYSTEM_PROMPT.lower()
        assert "answer" in SYSTEM_PROMPT.lower()

    def test_rag_prompt_template_not_empty(self):
        """Test that RAG_PROMPT_TEMPLATE is not empty."""
        assert RAG_PROMPT_TEMPLATE
        assert len(RAG_PROMPT_TEMPLATE) > 0

    def test_rag_prompt_template_has_placeholders(self):
        """Test that RAG_PROMPT_TEMPLATE has required placeholders."""
        assert "{context}" in RAG_PROMPT_TEMPLATE
        assert "{question}" in RAG_PROMPT_TEMPLATE
