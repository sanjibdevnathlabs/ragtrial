"""
Tests for RAG prompt engineering enhancements.

Verifies that prompts do not leak document references to LLM responses.
"""

import pytest
from langchain_core.documents import Document

from app.chain_rag.prompts import format_context, create_rag_prompt, SYSTEM_PROMPT


class TestFormatContext:
    """Tests for format_context function."""

    def test_format_context_no_document_numbers(self):
        """Test that formatted context does not include document numbers."""
        docs = [
            Document(
                page_content="Content 1",
                metadata={"source": "file1.pdf", "chunk": 0},
            ),
            Document(
                page_content="Content 2",
                metadata={"source": "file2.pdf", "chunk": 0},
            ),
        ]

        context = format_context(docs)

        assert "Document 1" not in context
        assert "Document 2" not in context
        assert "Content 1" in context
        assert "Content 2" in context

    def test_format_context_no_source_metadata(self):
        """Test that source metadata is not exposed in context."""
        docs = [
            Document(
                page_content="Test content",
                metadata={"source": "test.pdf", "filename": "test.pdf"},
            )
        ]

        context = format_context(docs)

        assert "source" not in context.lower()
        assert "test.pdf" not in context
        assert "Test content" in context

    def test_format_context_empty_documents(self):
        """Test formatting with empty document list."""
        context = format_context([])
        assert context == ""

    def test_format_context_separator(self):
        """Test that documents are separated properly."""
        docs = [
            Document(page_content="First doc"),
            Document(page_content="Second doc"),
        ]

        context = format_context(docs)

        assert "---" in context
        assert "First doc" in context
        assert "Second doc" in context

    def test_format_context_strips_whitespace(self):
        """Test that content whitespace is stripped."""
        docs = [
            Document(page_content="  Content with spaces  \n\n"),
        ]

        context = format_context(docs)

        assert context == "Content with spaces"


class TestSystemPrompt:
    """Tests for system prompt content."""

    def test_system_prompt_has_response_formatting_rules(self):
        """Test that system prompt includes formatting rules."""
        assert "RESPONSE FORMATTING RULES" in SYSTEM_PROMPT
        assert "NEVER mention document numbers" in SYSTEM_PROMPT
        assert "Integrate information seamlessly" in SYSTEM_PROMPT

    def test_system_prompt_prohibits_document_references(self):
        """Test that prompt explicitly prohibits document references."""
        prohibited_patterns = [
            "Document 1",
            "Document 5",
            "Chunk 0",
            "According to Document",
        ]

        for pattern in prohibited_patterns:
            assert (
                pattern in SYSTEM_PROMPT
            ), f"Prompt should mention prohibiting '{pattern}'"

    def test_system_prompt_requires_natural_synthesis(self):
        """Test that prompt requires natural answer synthesis."""
        assert "Synthesize information naturally" in SYSTEM_PROMPT
        assert "conversational answers" in SYSTEM_PROMPT


class TestRAGPrompt:
    """Tests for RAG prompt template creation."""

    def test_create_rag_prompt_structure(self):
        """Test that RAG prompt has correct structure."""
        prompt = create_rag_prompt()

        messages = prompt.format_messages(
            context="Test context", question="Test question"
        )

        assert len(messages) == 2
        assert messages[0].type == "system"
        assert messages[1].type == "human"

    def test_create_rag_prompt_system_message(self):
        """Test that system message contains full instructions."""
        prompt = create_rag_prompt()

        messages = prompt.format_messages(
            context="Test context", question="Test question"
        )

        system_content = messages[0].content

        assert "RESPONSE FORMATTING RULES" in system_content
        assert "NEVER mention document numbers" in system_content

    def test_create_rag_prompt_human_message(self):
        """Test that human message contains context and question."""
        prompt = create_rag_prompt()
        test_context = "This is test context"
        test_question = "What is this about?"

        messages = prompt.format_messages(
            context=test_context, question=test_question
        )

        human_content = messages[1].content

        assert test_context in human_content
        assert test_question in human_content


class TestDocumentReferenceDetection:
    """Tests for detecting document references in text."""

    @pytest.mark.parametrize(
        "text,should_contain_reference",
        [
            ("Document 1 says X", True),
            ("According to Document 5", True),
            ("As stated in Document 3", True),
            ("(Document 1, Document 5)", True),
            ("Chunk 0 contains", True),
            ("The answer is X", False),
            ("Based on the information provided", False),
            ("The system works as follows", False),
        ],
    )
    def test_detect_document_references(self, text, should_contain_reference):
        """Test detection of document references in text."""
        reference_patterns = [
            "Document ",
            "Chunk ",
            "According to Document",
            "As stated in Document",
        ]

        has_reference = any(pattern in text for pattern in reference_patterns)

        assert has_reference == should_contain_reference


class TestContextIntegration:
    """Integration tests for context formatting."""

    def test_multiple_documents_integration(self):
        """Test formatting multiple documents with metadata."""
        docs = [
            Document(
                page_content="Apache Kafka is a streaming platform.",
                metadata={
                    "source": "kafka_guide.pdf",
                    "filename": "kafka_guide.pdf",
                    "chunk": 0,
                },
            ),
            Document(
                page_content="Kafka handles real-time data streams.",
                metadata={
                    "source": "kafka_guide.pdf",
                    "filename": "kafka_guide.pdf",
                    "chunk": 1,
                },
            ),
            Document(
                page_content="It is used by many companies.",
                metadata={
                    "source": "kafka_overview.pdf",
                    "filename": "kafka_overview.pdf",
                    "chunk": 0,
                },
            ),
        ]

        context = format_context(docs)

        # Should contain all content
        assert "Apache Kafka is a streaming platform" in context
        assert "Kafka handles real-time data streams" in context
        assert "It is used by many companies" in context

        # Should NOT contain metadata
        assert "kafka_guide.pdf" not in context
        assert "chunk" not in context.lower()
        assert "Document" not in context

        # Should have separators
        assert context.count("---") == 2  # 3 docs = 2 separators

    def test_real_world_scenario(self):
        """Test with realistic document content."""
        docs = [
            Document(
                page_content=(
                    "Apache Kafka is a distributed streaming platform that allows "
                    "you to publish, subscribe to, store, and process streams of "
                    "data in real-time."
                ),
                metadata={"source": "doc1.pdf", "page": 1},
            ),
            Document(
                page_content=(
                    "Kafka is designed to handle continuous flow of data and treats "
                    "data as a continually evolving and ever-growing stream."
                ),
                metadata={"source": "doc2.pdf", "page": 5},
            ),
        ]

        context = format_context(docs)

        # Verify content is present
        assert "Apache Kafka is a distributed streaming platform" in context
        assert "Kafka is designed to handle continuous flow" in context

        # Verify no metadata leakage
        assert "doc1.pdf" not in context
        assert "doc2.pdf" not in context
        assert "page" not in context.lower()
        assert "Document 1" not in context
        assert "Document 2" not in context

        # Verify clean separation
        parts = context.split("---")
        assert len(parts) == 2
        assert all(part.strip() for part in parts)

