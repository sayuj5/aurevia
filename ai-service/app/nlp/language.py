"""
Language detection abstraction for the Aurevia NLP pipeline.

Uses a lightweight heuristic approach for the hackathon phase.
The interface is designed to be replaced by a proper detector later.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class LanguageDetectionResult:
    """Result from a language detector."""
    code: str          # ISO 639-1 code, e.g. "en"
    name: str          # Human-readable, e.g. "English"
    confidence: float  # 0.0 – 1.0


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseLanguageDetector(ABC):
    """Abstract language detector interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Detector name."""
        ...

    @abstractmethod
    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Detect the language of the provided text.

        Args:
            text: Normalised input text.

        Returns:
            LanguageDetectionResult with code, name and confidence.
        """
        ...


# ---------------------------------------------------------------------------
# Heuristic implementation (no external dependencies)
# ---------------------------------------------------------------------------

# Common words per language — lightweight heuristic
_LANGUAGE_SIGNATURES: dict[str, tuple[str, list[str]]] = {
    "en": ("English", ["the", "and", "is", "in", "of", "to", "a", "that", "it", "was"]),
    "es": ("Spanish", ["el", "la", "de", "en", "y", "que", "un", "una", "con", "por"]),
    "fr": ("French", ["le", "la", "de", "et", "en", "un", "une", "du", "les", "des"]),
    "de": ("German", ["der", "die", "das", "und", "in", "ist", "ein", "eine", "zu", "den"]),
    "hi": ("Hindi",  ["है", "में", "का", "के", "और", "को", "से", "एक", "पर", "यह"]),
}


class HeuristicLanguageDetector(BaseLanguageDetector):
    """
    Simple word-frequency heuristic language detector.

    Suitable for common European languages with Latin scripts.
    Falls back to "unknown" when confidence is too low.

    Replace with langdetect or fastText in production.
    """

    _MIN_CONFIDENCE: float = 0.25

    @property
    def name(self) -> str:
        return "heuristic-language-detector"

    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Detect language via word overlap heuristic.

        Args:
            text: Normalised text.

        Returns:
            LanguageDetectionResult.
        """
        words = set(text.lower().split())
        best_code = "unknown"
        best_name = "Unknown"
        best_score: float = 0.0

        for code, (lang_name, signatures) in _LANGUAGE_SIGNATURES.items():
            matches = sum(1 for w in signatures if w in words)
            score = matches / len(signatures)
            if score > best_score:
                best_score = score
                best_code = code
                best_name = lang_name

        if best_score < self._MIN_CONFIDENCE:
            best_code = "unknown"
            best_name = "Unknown"
            best_score = 0.0

        logger.debug(
            "Language detection: code=%s confidence=%.2f", best_code, best_score
        )
        return LanguageDetectionResult(
            code=best_code,
            name=best_name,
            confidence=round(best_score, 4),
        )


# ---------------------------------------------------------------------------
# Module-level default instance
# ---------------------------------------------------------------------------

_default_detector: BaseLanguageDetector = HeuristicLanguageDetector()


def get_detector() -> BaseLanguageDetector:
    """Return the active language detector."""
    return _default_detector


def detect_language(text: str) -> LanguageDetectionResult:
    """
    Convenience function: detect language using the active detector.

    Args:
        text: Normalised input text.

    Returns:
        LanguageDetectionResult.
    """
    return _default_detector.detect(text)
