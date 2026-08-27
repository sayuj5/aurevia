"""
Pydantic schemas for the Audio analysis API.

Response models for POST /api/v1/audio/analyze.
"""

from pydantic import BaseModel
from typing import Dict, Optional, Any


class FileInfo(BaseModel):
    """Metadata about the uploaded file."""
    object_id: str
    filename: str
    content_type: str
    size_bytes: int


class AudioMetadataInfo(BaseModel):
    """Basic audio metadata."""
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str


class AudioFeaturesInfo(BaseModel):
    """Extracted audio features."""
    rms: float
    zero_crossing_rate: float
    is_demo: bool
    additional: Dict[str, Any] = {}


class TranscriptionInfo(BaseModel):
    """Transcription result — placeholder until Phase 8+."""
    available: bool
    text: Optional[str] = None
    provider: Optional[str] = None


class StorageInfo(BaseModel):
    """Object storage metadata."""
    provider: str        # "local" | "minio"
    mode: str            # "demo" | "production"
    object_key: Optional[str] = None


class AudioAnalyzeResponse(BaseModel):
    """Full response from POST /api/v1/audio/analyze."""
    success: bool
    file: FileInfo
    audio: AudioMetadataInfo
    features: AudioFeaturesInfo
    transcription: TranscriptionInfo
    storage: StorageInfo
