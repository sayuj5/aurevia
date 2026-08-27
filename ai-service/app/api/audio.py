"""
Audio API router — POST /api/v1/audio/analyze

Accepts a multipart/form-data file upload, runs the audio pipeline,
and returns a structured JSON result.

Security notes:
  - The original filename is sanitised before use.
  - File bytes are validated before any processing.
  - Content is never logged.
  - Internal paths are never exposed.
"""

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse

from app.audio.service import run_audio_pipeline
from app.core.config import settings
from app.core.exceptions import AIException
from app.core.logging import logger
from app.schemas.audio import AudioAnalyzeResponse

router = APIRouter()

# Maximum bytes read from the upload stream (guard against huge files
# before the validator runs — set to 2× config limit as safety margin)
_MAX_READ_BYTES = settings.AUDIO_MAX_SIZE_MB * 1024 * 1024 * 2


@router.post(
    "/audio/analyze",
    response_model=AudioAnalyzeResponse,
    summary="Upload and analyze an audio file",
    description=(
        "Accepts a multipart audio file upload. "
        "Validates the file, stores it in object storage, extracts basic "
        "audio metadata and features, and returns a structured result. "
        "In DEMO_MODE all processing runs without external services."
    ),
    responses={
        200: {"description": "Audio analysis complete"},
        422: {"description": "File validation failed"},
        413: {"description": "File too large"},
        500: {"description": "Internal pipeline error"},
    },
)
async def audio_analyze(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, OGG, M4A, FLAC)"),
) -> AudioAnalyzeResponse:
    """
    POST /api/v1/audio/analyze

    Process an uploaded audio file through the full audio pipeline.
    """
    logger.info("Audio analyze endpoint called (DEMO_MODE=%s)", settings.DEMO_MODE)

    # Read file bytes (FastAPI streams, we materialise here)
    try:
        data = await file.read(_MAX_READ_BYTES)
    except Exception as exc:
        raise AIException(
            code="AUDIO_READ_FAILED",
            message="Failed to read uploaded file.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    filename = file.filename or "unknown"
    content_type = file.content_type or "application/octet-stream"

    result = run_audio_pipeline(filename, content_type, data)
    return result
