"""
Text preprocessing module for the Aurevia NLP pipeline.

Handles normalization, cleaning, and basic text metrics.
Raw user text is NEVER logged.
"""

import re
import unicodedata
from app.core.config import settings
from app.core.logging import logger

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_TEXT_LENGTH: int = 10_000  # characters


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class PreprocessingResult:
    """Result of text preprocessing."""

    def __init__(
        self,
        normalized_text: str,
        character_count: int,
        word_count: int,
        sentence_count: int,
    ) -> None:
        self.normalized_text = normalized_text
        self.character_count = character_count
        self.word_count = word_count
        self.sentence_count = sentence_count


def preprocess(text: str) -> PreprocessingResult:
    """
    Run the full preprocessing pipeline on input text.

    Steps:
      1. Unicode normalization (NFC)
      2. Remove control characters (preserve printable + newline/tab)
      3. Whitespace normalization
      4. Compute basic metrics

    Args:
        text: Raw input text (already validated as non-empty).

    Returns:
        PreprocessingResult with normalised text and metrics.
    """
    logger.debug("NLP preprocessing started (input length: %d chars)", len(text))

    text = _normalize_unicode(text)
    text = _remove_control_characters(text)
    text = _normalize_whitespace(text)

    char_count = len(text)
    word_count = _count_words(text)
    sentence_count = _count_sentences(text)

    logger.debug(
        "NLP preprocessing complete: chars=%d words=%d sentences=%d",
        char_count,
        word_count,
        sentence_count,
    )

    return PreprocessingResult(
        normalized_text=text,
        character_count=char_count,
        word_count=word_count,
        sentence_count=sentence_count,
    )


def validate_length(text: str) -> None:
    """
    Raise ValueError if text exceeds the maximum allowed length.

    Args:
        text: Input text to check.

    Raises:
        ValueError: If text is too long.
    """
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"Input text exceeds maximum length of {MAX_TEXT_LENGTH} characters "
            f"(received {len(text)} characters)."
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _normalize_unicode(text: str) -> str:
    """Apply NFC unicode normalization."""
    return unicodedata.normalize("NFC", text)


def _remove_control_characters(text: str) -> str:
    """
    Remove non-printable control characters while preserving:
      - Standard whitespace: space, tab, newline, carriage return
      - All printable characters
    """
    result = []
    for char in text:
        cat = unicodedata.category(char)
        if char in (" ", "\t", "\n", "\r"):
            result.append(char)
        elif cat.startswith("C"):
            # Control character — drop it
            continue
        else:
            result.append(char)
    return "".join(result)


def _normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace:
      - Replace tab characters with a single space
      - Collapse multiple consecutive spaces into one
      - Strip leading/trailing whitespace from the whole string
      - Preserve single newlines (sentence boundaries)
    """
    # Replace tabs with space
    text = text.replace("\t", " ")
    # Collapse multiple spaces into one (but not newlines)
    text = re.sub(r" {2,}", " ", text)
    # Strip leading/trailing
    text = text.strip()
    return text


def _count_words(text: str) -> int:
    """Count words by whitespace splitting."""
    return len(text.split())


def _count_sentences(text: str) -> int:
    """
    Estimate sentence count using simple punctuation-based heuristic.
    This is intentionally a lightweight approximation.
    """
    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    parts = re.split(r"[.!?]+(?:\s|$)", text)
    # Filter out empty fragments
    return max(1, len([p for p in parts if p.strip()]))
