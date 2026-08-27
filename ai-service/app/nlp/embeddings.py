"""
Embeddings abstraction for the Aurevia NLP pipeline.

Defines the interface and a DEMO_MODE implementation that produces
deterministic placeholder vectors without any model downloads.

A real Sentence Transformer provider can be introduced later without
changing the public API.
"""

import hashlib
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class EmbeddingResult:
    """Result from an embedding provider."""
    provider: str
    dimensions: int
    vector: List[float]
    is_demo: bool


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseEmbeddingProvider(ABC):
    """Abstract embedding provider interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Embedding vector size."""
        ...

    @abstractmethod
    def embed(self, text: str) -> EmbeddingResult:
        """
        Produce an embedding vector for the given text.

        Args:
            text: Preprocessed text to embed.

        Returns:
            EmbeddingResult with vector and metadata.
        """
        ...


# ---------------------------------------------------------------------------
# Demo implementation (no ML dependencies, fully deterministic)
# ---------------------------------------------------------------------------

_DEMO_DIMENSIONS = 64  # Small but illustrative


class DemoEmbeddingProvider(BaseEmbeddingProvider):
    """
    DEMO_MODE embedding provider.

    Produces a deterministic, hash-derived pseudo-embedding vector.
    Vectors are reproducible for the same input text.

    Clearly marked as demo — NOT suitable for semantic similarity.
    Replace with SentenceTransformers in a later phase.
    """

    _NAME = "aurevia-demo-embeddings"

    @property
    def name(self) -> str:
        return self._NAME

    @property
    def dimensions(self) -> int:
        return _DEMO_DIMENSIONS

    def embed(self, text: str) -> EmbeddingResult:
        """
        Produce a deterministic demo embedding.

        Uses SHA-256 of the input to seed a normalized pseudo-random vector.
        Guaranteed reproducible for the same input.

        Args:
            text: Input text.

        Returns:
            EmbeddingResult.
        """
        vector = self._hash_to_vector(text)
        logger.debug(
            "DemoEmbeddingProvider.embed: dims=%d is_demo=True", self.dimensions
        )
        return EmbeddingResult(
            provider=self._NAME,
            dimensions=self.dimensions,
            vector=vector,
            is_demo=True,
        )

    def _hash_to_vector(self, text: str) -> List[float]:
        """
        Derive a stable, normalised float vector from text via SHA-256.

        Each 4 bytes of the hash seed one float component in [-1, 1].
        The process cycles over the hash bytes to fill all dimensions.
        """
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector: List[float] = []
        digest_len = len(digest)

        for i in range(self.dimensions):
            # Use 4 bytes per component, cycling through digest
            start = (i * 4) % (digest_len - 3)
            raw = int.from_bytes(digest[start : start + 4], byteorder="big", signed=True)
            # Normalize to [-1.0, 1.0]
            normalized = raw / (2**31)
            vector.append(round(normalized, 6))

        return vector


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """
    Real Embedding Provider using SentenceTransformers.
    Generates semantic vectors for text.
    Loads lazily via the global model_manager.
    """
    
    def __init__(self, model_name: str, device: str = "cpu") -> None:
        self._model_name = model_name
        self._device_str = device
        self._dimensions = 384 # default for miniLM, could be fetched dynamically

        def _load_st():
            try:
                import torch
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise RuntimeError("Missing required dependencies for real embeddings (sentence-transformers, torch).")

            device_name = "cpu"
            if self._device_str.lower() in ("cuda", "gpu") and torch.cuda.is_available():
                device_name = "cuda"
            
            logger.info("Initializing SentenceTransformer: %s on %s", self._model_name, device_name)
            # Use trust_remote_code=False for security, unless specifically required by the model
            return SentenceTransformer(self._model_name, device=device_name)
            
        from app.models.manager import model_manager
        model_manager.register_loader(f"embedding_{self._model_name}", _load_st)

    @property
    def name(self) -> str:
        return f"sentence-transformers/{self._model_name}"

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> EmbeddingResult:
        if not text.strip():
            return EmbeddingResult(
                provider=self.name,
                dimensions=self.dimensions,
                vector=[0.0] * self.dimensions,
                is_demo=False,
            )

        from app.models.manager import model_manager
        
        try:
            model = model_manager.get_model(f"embedding_{self._model_name}")
            
            # SentenceTransformers handles tokenization and truncation internally
            # We encode the text and get a numpy array back
            embeddings = model.encode(text, convert_to_numpy=True)
            
            # Convert to float list for JSON serialization
            vector = [float(v) for v in embeddings]
            
            # Dynamically update dimensions if it's the first time
            if self._dimensions != len(vector):
                self._dimensions = len(vector)
                
            return EmbeddingResult(
                provider=self.name,
                dimensions=self.dimensions,
                vector=vector,
                is_demo=False,
            )
        except ImportError:
            logger.error("sentence-transformers or torch not installed. Cannot run SentenceTransformerEmbeddingProvider.")
            raise RuntimeError("Missing required dependencies for real embeddings (sentence-transformers, torch).")
        except Exception as exc:
            logger.error("SentenceTransformer inference failed: %s", exc)
            raise RuntimeError(f"Embedding generation failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Module-level default instance
# ---------------------------------------------------------------------------

_default_provider: BaseEmbeddingProvider = DemoEmbeddingProvider()


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Return the active embedding provider."""
    return _default_provider


def embed(text: str) -> EmbeddingResult:
    """
    Convenience function: embed text using the active provider.

    Args:
        text: Preprocessed text.

    Returns:
        EmbeddingResult.
    """
    return _default_provider.embed(text)
