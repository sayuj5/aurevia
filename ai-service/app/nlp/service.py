"""
NLP service — orchestrates the full NLP pipeline.

Coordinates: validation → preprocessing → tokenization
             → language detection → model analysis → embedding
"""

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AIException
from fastapi import status

from app.nlp.preprocess import preprocess, validate_length
from app.nlp.tokenizer import tokenize
from app.nlp.language import detect_language
from app.intelligence.service import resolve_nlp_model, resolve_embedding_provider

from app.schemas.nlp import (
    NLPAnalyzeResponse,
    LanguageInfo,
    PreprocessingInfo,
    TokensInfo,
    ModelInfo,
    EmbeddingInfo,
)


def run_nlp_pipeline(text: str) -> NLPAnalyzeResponse:
    """
    Execute the full NLP pipeline on validated input text.

    Pipeline stages:
      1. Length validation
      2. Text preprocessing (normalize, clean, metrics)
      3. Tokenization
      4. Language detection
      5. NLP model analysis
      6. Embedding

    Privacy: raw text is never logged.

    Args:
        text: Validated, non-empty input text.

    Returns:
        NLPAnalyzeResponse ready for serialization.

    Raises:
        AIException: On pipeline failure.
    """
    logger.info("NLP pipeline started (DEMO_MODE=%s)", settings.DEMO_MODE)

    # 1. Length validation
    try:
        validate_length(text)
    except ValueError as exc:
        raise AIException(
            code="NLP_INPUT_TOO_LONG",
            message=str(exc),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ) from exc

    # 2. Preprocessing
    try:
        prep = preprocess(text)
    except Exception as exc:
        logger.error("NLP preprocessing failed: %s", type(exc).__name__)
        raise AIException(
            code="NLP_PREPROCESSING_FAILED",
            message="Text preprocessing failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    # 3. Tokenization
    try:
        tokens = tokenize(prep.normalized_text)
    except Exception as exc:
        logger.error("Tokenization failed: %s", type(exc).__name__)
        raise AIException(
            code="NLP_TOKENIZATION_FAILED",
            message="Tokenization failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    # 4. Language detection
    try:
        lang = detect_language(prep.normalized_text)
    except Exception as exc:
        logger.error("Language detection failed: %s", type(exc).__name__)
        raise AIException(
            code="NLP_LANGUAGE_DETECTION_FAILED",
            message="Language detection failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    # 5. NLP model analysis
    try:
        nlp_model = resolve_nlp_model()
        model_result = nlp_model.analyze(prep.normalized_text, tokens)
    except Exception as exc:
        logger.error("NLP model analysis failed: %s", type(exc).__name__)
        raise AIException(
            code="NLP_MODEL_FAILED",
            message="NLP model analysis failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    # 6. Embedding
    try:
        embedding_provider = resolve_embedding_provider()
        embedding = embedding_provider.embed(prep.normalized_text)
    except Exception as exc:
        logger.error("Embedding failed: %s", type(exc).__name__)
        raise AIException(
            code="NLP_EMBEDDING_FAILED",
            message="Embedding generation failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    logger.info(
        "NLP pipeline complete: lang=%s tokens=%d dims=%d",
        lang.code,
        len(tokens),
        embedding.dimensions,
    )

    return NLPAnalyzeResponse(
        success=True,
        language=LanguageInfo(
            code=lang.code,
            name=lang.name,
            confidence=lang.confidence,
        ),
        preprocessing=PreprocessingInfo(
            character_count=prep.character_count,
            word_count=prep.word_count,
            sentence_count=prep.sentence_count,
        ),
        tokens=TokensInfo(
            count=len(tokens),
            items=tokens,
        ),
        model=ModelInfo(
            name=model_result.model_name,
            version=model_result.model_version,
            mode=model_result.mode,
        ),
        embedding=EmbeddingInfo(
            provider=embedding.provider,
            dimensions=embedding.dimensions,
            is_demo=embedding.is_demo,
        ),
    )
