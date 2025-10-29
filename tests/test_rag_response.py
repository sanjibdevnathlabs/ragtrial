"""
Tests for ResponseFormatter.

Tests response formatting and source extraction for RAG.
"""

from langchain_core.documents import Document

import constants
from app.chain_rag.response import ResponseFormatter


class TestResponseFormatterFormatResponse:
    """Tests for ResponseFormatter.format_response() method."""

    def test_format_response_with_answer_and_sources(self):
        """Test formatting response with answer and sources."""
        answer = "This is the answer to your question."
        documents = [
            Document(page_content="Content 1" * 100, metadata={"source": "doc1.txt"}),
            Document(page_content="Content 2" * 100, metadata={"source": "doc2.txt"}),
        ]
        query = "What is the answer?"

        response = ResponseFormatter.format_response(answer, documents, query)

        assert response[constants.RESPONSE_KEY_ANSWER] == answer
        assert response[constants.RESPONSE_KEY_QUERY] == query
        assert response[constants.RESPONSE_KEY_RETRIEVAL_COUNT] == 2
        assert response[constants.RESPONSE_KEY_HAS_ANSWER] is True
        assert len(response[constants.RESPONSE_KEY_SOURCES]) == 2

    def test_format_response_empty_documents(self):
        """Test formatting with no source documents."""
        answer = "I don't have information."
        documents = []
        query = "Test query"

        response = ResponseFormatter.format_response(answer, documents, query)

        assert response[constants.RESPONSE_KEY_RETRIEVAL_COUNT] == 0
        assert len(response[constants.RESPONSE_KEY_SOURCES]) == 0

    def test_format_response_no_answer_phrase(self):
        """Test formatting with 'no answer' phrase."""
        answer = "I don't have enough information to answer this question."
        documents = [Document(page_content="Test", metadata={"source": "test.txt"})]
        query = "Test?"

        response = ResponseFormatter.format_response(answer, documents, query)

        assert response[constants.RESPONSE_KEY_HAS_ANSWER] is False

    def test_format_response_all_required_keys_present(self):
        """Test that response contains all required keys."""
        response = ResponseFormatter.format_response(
            "Answer", [Document(page_content="Test", metadata={})], "Query"
        )

        assert constants.RESPONSE_KEY_ANSWER in response
        assert constants.RESPONSE_KEY_SOURCES in response
        assert constants.RESPONSE_KEY_QUERY in response
        assert constants.RESPONSE_KEY_RETRIEVAL_COUNT in response
        assert constants.RESPONSE_KEY_HAS_ANSWER in response


class TestResponseFormatterExtractSources:
    """Tests for ResponseFormatter._extract_sources() method."""

    def test_extract_sources_empty_list(self):
        """Test extracting sources from empty list."""
        sources = ResponseFormatter._extract_sources([])

        assert sources == []

    def test_extract_sources_single_document(self):
        """Test extracting source from single document."""
        docs = [
            Document(
                page_content="This is a long content " * 50,
                metadata={"source": "test.txt", "page": 1},
            )
        ]

        sources = ResponseFormatter._extract_sources(docs)

        assert len(sources) == 1
        assert "content" in sources[0]
        assert "metadata" in sources[0]
        assert sources[0]["metadata"]["source"] == "test.txt"
        assert sources[0]["metadata"]["page"] == 1

    def test_extract_sources_truncates_long_content(self):
        """Test that long content is truncated to 200 chars."""
        long_content = "A" * 500
        docs = [Document(page_content=long_content, metadata={"source": "test.txt"})]

        sources = ResponseFormatter._extract_sources(docs)

        assert len(sources[0]["content"]) == 200
        assert sources[0]["content"] == "A" * 200

    def test_extract_sources_multiple_documents(self):
        """Test extracting sources from multiple documents."""
        docs = [
            Document(page_content="Content 1", metadata={"source": "doc1.txt"}),
            Document(page_content="Content 2", metadata={"source": "doc2.txt"}),
            Document(page_content="Content 3", metadata={"source": "doc3.txt"}),
        ]

        sources = ResponseFormatter._extract_sources(docs)

        assert len(sources) == 3
        assert sources[0]["metadata"]["source"] == "doc1.txt"
        assert sources[1]["metadata"]["source"] == "doc2.txt"
        assert sources[2]["metadata"]["source"] == "doc3.txt"

    def test_extract_sources_preserves_all_metadata(self):
        """Test that all metadata is preserved."""
        docs = [
            Document(
                page_content="Content",
                metadata={
                    "source": "test.txt",
                    "page": 5,
                    "author": "John",
                    "custom_field": "value",
                },
            )
        ]

        sources = ResponseFormatter._extract_sources(docs)

        assert sources[0]["metadata"]["source"] == "test.txt"
        assert sources[0]["metadata"]["page"] == 5
        assert sources[0]["metadata"]["author"] == "John"
        assert sources[0]["metadata"]["custom_field"] == "value"


class TestResponseFormatterCheckHasAnswer:
    """Tests for ResponseFormatter._check_has_answer() method."""

    def test_check_has_answer_valid_answer(self):
        """Test check with valid answer."""
        answer = "The answer is 42."

        result = ResponseFormatter._check_has_answer(answer)

        assert result is True

    def test_check_has_answer_empty_string(self):
        """Test check with empty string."""
        result = ResponseFormatter._check_has_answer("")

        assert result is False

    def test_check_has_answer_whitespace_only(self):
        """Test check with whitespace only."""
        result = ResponseFormatter._check_has_answer("   ")

        assert result is False

    def test_check_has_answer_phrase_not_enough_info(self):
        """Test check with 'not enough information' phrase."""
        answer = "I don't have enough information to answer."

        result = ResponseFormatter._check_has_answer(answer)

        assert result is False

    def test_check_has_answer_phrase_cannot_answer(self):
        """Test check with 'cannot answer' phrase."""
        answer = "I cannot answer this question."

        result = ResponseFormatter._check_has_answer(answer)

        assert result is False

    def test_check_has_answer_phrase_insufficient_context(self):
        """Test check with 'insufficient context' phrase."""
        answer = "There is insufficient context to answer."

        result = ResponseFormatter._check_has_answer(answer)

        assert result is False

    def test_check_has_answer_phrase_no_information(self):
        """Test check with 'no information' phrase."""
        answer = "No information provided about this topic."

        result = ResponseFormatter._check_has_answer(answer)

        assert result is False

    def test_check_has_answer_case_insensitive(self):
        """Test that phrase checking is case insensitive."""
        answer = "I DON'T HAVE ENOUGH INFORMATION."

        result = ResponseFormatter._check_has_answer(answer)

        assert result is False

    def test_check_has_answer_partial_phrase_match(self):
        """Test that partial phrase matching works."""
        answer = "Unfortunately, I don't have enough information in the context."

        result = ResponseFormatter._check_has_answer(answer)

        assert result is False
