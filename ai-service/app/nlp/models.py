"""
NLP model abstraction for the Aurevia NLP pipeline.

Defines the interface and a DEMO_MODE implementation.
Real transformer-based models can be plugged in without
changing the public API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class NLPModelResult:
    """Structured output from an NLP model."""
    model_name: str
    model_version: str
    mode: str                          # "demo" | "production"
    indicators: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseNLPModel(ABC):
    """Abstract NLP model interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Model name identifier."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Model version string."""
        ...

    @abstractmethod
    def analyze(self, text: str, tokens: list[str]) -> NLPModelResult:
        """
        Run NLP analysis on the preprocessed text and tokens.

        Args:
            text:   Preprocessed/normalized text.
            tokens: Tokens produced by the tokenizer.

        Returns:
            NLPModelResult with indicators and metadata.
        """
        ...


# ---------------------------------------------------------------------------
# Demo implementation (no ML dependencies)
# ---------------------------------------------------------------------------

class DemoNLPModel(BaseNLPModel):
    """
    DEMO_MODE NLP model.

    Returns deterministic, plausible-looking output without requiring
    any model downloads or GPU.  Clearly marked as demo output.
    """

    _NAME = "aurevia-demo-nlp"
    _VERSION = "0.1.0-demo"

    @property
    def name(self) -> str:
        return self._NAME

    @property
    def version(self) -> str:
        return self._VERSION

    def analyze(self, text: str, tokens: list[str]) -> NLPModelResult:
        """
        Produce deterministic demo NLP indicators.

        Indicators are computed from basic text statistics only —
        no actual ML inference is performed.
        """
        word_count = len(tokens)
        avg_token_length = (
            sum(len(t) for t in tokens) / word_count if word_count else 0.0
        )

        indicators: Dict[str, Any] = {
            "token_count": word_count,
            "avg_token_length": round(avg_token_length, 2),
            "is_demo": True,
            "note": (
                "DEMO_MODE active. Indicators are derived from basic "
                "text statistics, not real model inference."
            ),
        }

        logger.debug(
            "DemoNLPModel.analyze complete: token_count=%d", word_count
        )

        return NLPModelResult(
            model_name=self._NAME,
            model_version=self._VERSION,
            mode="demo",
            indicators=indicators,
        )


class RealNLPModel(BaseNLPModel):
    """
    Real NLP Model using Hugging Face Transformers.
    Performs sentiment/classification analysis depending on the loaded model.
    Loads lazily via the global model_manager.
    """

    def __init__(self, model_name: str, device: str = "cpu") -> None:
        self._model_name = model_name
        self._device_str = device
        
        # We define a loader function for the model manager
        def _load_pipeline():
            import torch
            from transformers import pipeline
            
            # Map device string to torch device or pipeline device int
            device_id = -1 # default CPU for pipeline
            if self._device_str.lower() in ("cuda", "gpu") and torch.cuda.is_available():
                device_id = 0
            
            logger.info("Initializing HuggingFace pipeline for text-classification: %s on device %s", self._model_name, device_id)
            return pipeline(
                "text-classification",
                model=self._model_name,
                device=device_id
            )

        from app.models.manager import model_manager
        model_manager.register_loader(f"nlp_{self._model_name}", _load_pipeline)

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def version(self) -> str:
        return "1.0.0-hf"

    def analyze(self, text: str, tokens: list[str]) -> NLPModelResult:
        if not text.strip():
            return NLPModelResult(
                model_name=self.name,
                model_version=self.version,
                mode="production",
                indicators={}
            )

        from app.models.manager import model_manager
        
        try:
            # Lazy load / get cached pipeline
            classifier = model_manager.get_model(f"nlp_{self._model_name}")
            
            # Max length truncation (most bert models are 512 tokens max)
            # We truncate by chars as a very rough safety heuristic before passing to pipeline
            # The pipeline usually handles its own truncation if configured, but we wrap it safely
            safe_text = text[:2000]
            
            # Inference
            outputs = classifier(safe_text, truncation=True, max_length=512)
            
            # Extract results (pipeline returns list of dicts: [{'label': 'POSITIVE', 'score': 0.99}])
            indicators = {}
            if outputs and isinstance(outputs, list):
                for idx, out in enumerate(outputs):
                    label = out.get('label', f'label_{idx}')
                    score = out.get('score', 0.0)
                    indicators[label] = round(float(score), 4)

            return NLPModelResult(
                model_name=self.name,
                model_version=self.version,
                mode="production",
                indicators=indicators,
            )
            
        except ImportError:
            logger.error("transformers or torch not installed. Cannot run RealNLPModel.")
            raise RuntimeError("Missing required dependencies for RealNLPModel (transformers, torch).")
        except Exception as exc:
            logger.error("RealNLPModel inference failed: %s", exc)
            raise RuntimeError(f"NLP inference failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Module-level default instance
# ---------------------------------------------------------------------------

_default_model: BaseNLPModel = DemoNLPModel()


def get_nlp_model() -> BaseNLPModel:
    """Return the active NLP model."""
    return _default_model
