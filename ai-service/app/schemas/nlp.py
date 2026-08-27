"""
Pydantic schemas for the NLP analysis API.

Request and response models for POST /api/v1/nlp/analyze.
"""

from pydantic import BaseModel, field_validator
from typing import List, Optional


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class NLPAnalyzeRequest(BaseModel):
    """Request body for the NLP analysis endpoint."""

    text: str

    @field_validator("text", mode="before")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("text must be a string")
        if not v.strip():
            raise ValueError("text must not be empty or whitespace-only")
        return v


# ---------------------------------------------------------------------------
# Response sub-models
# ---------------------------------------------------------------------------

class LanguageInfo(BaseModel):
    """Language detection result."""

    code: str
    name: str
    confidence: float


class PreprocessingInfo(BaseModel):
    """Preprocessing metadata."""

    character_count: int
    word_count: int
    sentence_count: int


class TokensInfo(BaseModel):
    """Tokenization result."""

    count: int
    items: List[str]


class ModelInfo(BaseModel):
    """NLP model metadata."""

    name: str
    version: str
    mode: str  # "demo" or "production"


class EmbeddingInfo(BaseModel):
    """Embedding metadata."""

    provider: str
    dimensions: int
    is_demo: bool


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------

class NLPAnalyzeResponse(BaseModel):
    """Response from the NLP analysis endpoint."""

    success: bool
    language: LanguageInfo
    preprocessing: PreprocessingInfo
    tokens: TokensInfo
    model: ModelInfo
    embedding: EmbeddingInfo
