"""
Tokenizer abstraction for the Aurevia NLP pipeline.

Provides a replaceable tokenizer interface. The default implementation
uses Python's standard library only — no heavy NLP dependencies required.
"""

import re
from abc import ABC, abstractmethod
from typing import List
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseTokenizer(ABC):
    """Abstract tokenizer interface. Implementations must be thread-safe."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable tokenizer name."""
        ...

    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize the given text.

        Args:
            text: Preprocessed text.

        Returns:
            List of token strings. Empty list for empty input.
        """
        ...


# ---------------------------------------------------------------------------
# Default lightweight implementation
# ---------------------------------------------------------------------------

class SimpleTokenizer(BaseTokenizer):
    """
    Lightweight word tokenizer using regex.

    Splits on whitespace and handles punctuation as separate tokens.
    Replaceable by a Hugging Face / spaCy tokenizer in a later phase.
    """

    @property
    def name(self) -> str:
        return "simple-regex-tokenizer"

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize by splitting on whitespace, keeping punctuation attached
        to words where it forms natural contractions but otherwise separating it.

        Args:
            text: Input text.

        Returns:
            List of tokens.
        """
        if not text or not text.strip():
            return []

        # Match word characters and apostrophes (contractions) OR punctuation
        tokens = re.findall(r"[\w']+|[.,!?;:\"()\[\]{}\-/\\@#$%^&*]", text)
        logger.debug("Tokenizer produced %d tokens", len(tokens))
        return tokens


# ---------------------------------------------------------------------------
# Module-level default instance
# ---------------------------------------------------------------------------

_default_tokenizer: BaseTokenizer = SimpleTokenizer()


def get_tokenizer() -> BaseTokenizer:
    """Return the active tokenizer instance."""
    return _default_tokenizer


def tokenize(text: str) -> List[str]:
    """
    Convenience function: tokenize text using the active tokenizer.

    Args:
        text: Preprocessed text.

    Returns:
        List of tokens.
    """
    return _default_tokenizer.tokenize(text)
