"""
AI Intelligence Orchestration Service.

Coordinates NLP, Embeddings, and Audio processing.
Determines whether to use real models or demo models based on config.
"""

from app.core.config import settings
from app.core.logging import logger

from app.nlp.models import get_nlp_model, BaseNLPModel, RealNLPModel, DemoNLPModel
from app.nlp.embeddings import get_embedding_provider, BaseEmbeddingProvider, SentenceTransformerEmbeddingProvider, DemoEmbeddingProvider
from app.audio.transcription import get_transcription_provider, BaseTranscriptionProvider, WhisperTranscriptionProvider, DemoTranscriptionProvider


def resolve_nlp_model() -> BaseNLPModel:
    """Resolve which NLP model to use based on configuration."""
    if settings.AI_MODE.lower() == "real":
        logger.debug("Resolving Real NLP Model")
        return RealNLPModel(
            model_name=settings.NLP_MODEL_NAME,
            device=settings.AI_DEVICE
        )
    return DemoNLPModel()


def resolve_embedding_provider() -> BaseEmbeddingProvider:
    """Resolve which embedding provider to use."""
    if settings.AI_MODE.lower() == "real":
        logger.debug("Resolving Real Embedding Provider")
        return SentenceTransformerEmbeddingProvider(
            model_name=settings.EMBEDDING_MODEL_NAME,
            device=settings.AI_DEVICE
        )
    return DemoEmbeddingProvider()


def resolve_transcription_provider() -> BaseTranscriptionProvider:
    """Resolve which transcription provider to use."""
    if settings.AI_MODE.lower() == "real":
        logger.debug("Resolving Real Transcription Provider")
        return WhisperTranscriptionProvider(
            model_name=settings.STT_MODEL_NAME,
            device=settings.AI_DEVICE
        )
    return DemoTranscriptionProvider()


# We will patch the service layers of NLP and Audio to use these resolvers
# when they need a model, instead of the hardcoded default demo ones.
