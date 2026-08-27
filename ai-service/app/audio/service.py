"""
Audio service — orchestrates the full audio processing pipeline.

Pipeline:
  1. Validate file (extension, MIME, size, magic bytes)
  2. Upload to object storage
  3. Extract audio metadata
  4. Extract audio features
  5. Run transcription (Phase 3: stub)
  6. Return structured result

Raw filenames are never used for storage paths.
Audio content is never logged.
"""

import uuid
from datetime import datetime, timezone

from fastapi import status

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AIException

from app.audio.validator import AudioFileValidator, AudioValidationError
from app.audio.metadata import AudioMetadataExtractor
from app.audio.features import AudioFeatureExtractor
from app.intelligence.service import resolve_transcription_provider

from app.storage.minio import get_storage
from app.schemas.audio import (
    AudioAnalyzeResponse,
    FileInfo,
    AudioMetadataInfo,
    AudioFeaturesInfo,
    TranscriptionInfo,
    StorageInfo,
)

_validator = AudioFileValidator()
_metadata_extractor = AudioMetadataExtractor()
_feature_extractor = AudioFeatureExtractor()


def run_audio_pipeline(
    filename: str,
    content_type: str,
    data: bytes,
) -> AudioAnalyzeResponse:
    """
    Execute the full audio analysis pipeline.

    Args:
        filename:     Original filename from upload (untrusted).
        content_type: Declared MIME type (untrusted).
        data:         Raw audio bytes.

    Returns:
        AudioAnalyzeResponse.

    Raises:
        AIException: On any pipeline failure.
    """
    logger.info(
        "Audio pipeline started: declared_ct=%s size=%d bytes DEMO=%s",
        content_type, len(data), settings.DEMO_MODE,
    )

    # 1. Validation
    try:
        validation = _validator.validate(filename, content_type, data)
    except AudioValidationError as exc:
        raise AIException(
            code=exc.code,
            message=exc.message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ) from exc

    # 2. Object storage
    object_key = _make_object_key(validation.safe_extension)
    try:
        storage = get_storage()
        stored = storage.upload(object_key, data, validation.declared_content_type)
    except Exception as exc:
        logger.error("Storage upload failed: %s", type(exc).__name__)
        raise AIException(
            code="AUDIO_STORAGE_FAILED",
            message="Failed to store audio file.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    # 3. Metadata
    try:
        meta = _metadata_extractor.extract(data, validation.detected_format)
    except Exception as exc:
        logger.warning("Metadata extraction failed: %s", exc)
        from app.audio.metadata import AudioMetadata
        meta = AudioMetadata(
            duration_seconds=0.0, sample_rate=0, channels=0,
            format=validation.detected_format,
        )

    # 4. Features
    try:
        features = _feature_extractor.extract(data, validation.detected_format, meta.sample_rate)
    except Exception as exc:
        logger.warning("Feature extraction failed: %s", exc)
        from app.audio.features import AudioFeatures
        features = AudioFeatures(rms=0.0, zero_crossing_rate=0.0, is_demo=True)

    # 5. Transcription
    transcription_provider = resolve_transcription_provider()
    try:
        transcription = transcription_provider.transcribe(
            data, validation.detected_format, meta.sample_rate
        )
    except Exception as exc:
        logger.warning("Transcription failed: %s", exc)
        from app.audio.transcription import TranscriptionResult
        transcription = TranscriptionResult(available=False, text=None, provider=None)

    logger.info(
        "Audio pipeline complete: key=%s fmt=%s dur=%.2fs",
        stored.object_key, validation.detected_format, meta.duration_seconds,
    )

    storage_mode = "demo" if settings.DEMO_MODE else "production"

    return AudioAnalyzeResponse(
        success=True,
        file=FileInfo(
            object_id=stored.object_key,
            filename=validation.original_filename,
            content_type=stored.content_type,
            size_bytes=stored.size_bytes,
        ),
        audio=AudioMetadataInfo(
            duration_seconds=meta.duration_seconds,
            sample_rate=meta.sample_rate,
            channels=meta.channels,
            format=meta.format,
        ),
        features=AudioFeaturesInfo(
            rms=features.rms,
            zero_crossing_rate=features.zero_crossing_rate,
            is_demo=features.is_demo,
            additional=features.additional,
        ),
        transcription=TranscriptionInfo(
            available=transcription.available,
            text=transcription.text,
            provider=transcription.provider,
        ),
        storage=StorageInfo(
            provider=storage.provider_name,
            mode=storage_mode,
            object_key=stored.object_key,
        ),
    )


def _make_object_key(extension: str) -> str:
    """
    Generate a safe, unique object key.

    Format: audio/<date>/<uuid>.<ext>
    Never derived from the original filename.
    """
    today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    uid = uuid.uuid4().hex
    return f"audio/{today}/{uid}.{extension}"
