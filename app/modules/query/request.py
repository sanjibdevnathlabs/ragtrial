"""
Query module request models.

Contains Pydantic models for RAG query requests.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator

import constants


class QueryRequest(BaseModel):
    """Request model for RAG query."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"question": "What is retrieval-augmented generation?"}
        }
    )

    question: str = Field(
        ...,
        min_length=constants.MIN_QUERY_LENGTH,
        max_length=constants.MAX_QUERY_LENGTH_API,
        description="Question to ask the RAG system",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question is not empty or too short."""
        if not v or not v.strip():
            raise ValueError(constants.ERROR_QUERY_EMPTY)

        if len(v.strip()) < constants.MIN_QUERY_LENGTH:
            raise ValueError(constants.ERROR_QUERY_TOO_SHORT)

        return v.strip()
