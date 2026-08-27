"""
Audio file validator.

Validates uploaded audio files using a layered approach:
  1. Filename / extension check
  2. Declared content-type check
  3. File size check
  4. Magic-byte (file header) verification

Raw filenames are NEVER used for storage path construction.
All validation errors raise AudioValidationError with structured details.
"""

import os
from dataclasses import dataclass
from typing import Tuple

from app.core.config import settings
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Custom validation exception (maps to AIException at the service layer)
# ---------------------------------------------------------------------------

class AudioValidationError(Exception):
    """Raised when an uploaded audio file fails validation."""
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


# ---------------------------------------------------------------------------
# Magic byte signatures for supported formats
# ---------------------------------------------------------------------------

_MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    "wav":  [b"RIFF"],          # RIFF....WAVE
    "mp3":  [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2", b"ID3"],
    "ogg":  [b"OggS"],
    "flac": [b"fLaC"],
    "m4a":  [b"ftyp"],          # at offset 4
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Outcome of a successful validation."""
    original_filename: str      # kept for logging/metadata only
    safe_extension: str         # validated extension
    declared_content_type: str
    size_bytes: int
    detected_format: str        # format identified by magic bytes


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class AudioFileValidator:
    """Validates audio file uploads before any processing."""

    def validate(
        self,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> ValidationResult:
        """
        Full validation pipeline.

        Args:
            filename:     Original filename from the multipart upload (untrusted).
            content_type: Declared MIME type from the multipart upload (untrusted).
            data:         Raw file bytes.

        Returns:
            ValidationResult if all checks pass.

        Raises:
            AudioValidationError: On any validation failure.
        """
        # 1. Filename safety
        safe_name = self._sanitise_filename(filename)

        # 2. Extension check
        ext = self._validate_extension(safe_name)

        # 3. Content-type check
        self._validate_content_type(content_type)

        # 4. Size check
        self._validate_size(data)

        # 5. Magic-byte check (must not be empty)
        if not data:
            raise AudioValidationError(
                "AUDIO_EMPTY_FILE",
                "Uploaded file is empty.",
            )
        detected = self._detect_format(data, ext)

        logger.debug(
            "AudioValidator: ext=%s declared_ct=%s size=%d detected=%s",
            ext, content_type, len(data), detected,
        )

        return ValidationResult(
            original_filename=safe_name,
            safe_extension=ext,
            declared_content_type=content_type,
            size_bytes=len(data),
            detected_format=detected,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitise_filename(filename: str) -> str:
        """
        Strip directory components and limit length.
        Prevents path traversal from the filename itself.
        """
        if not filename:
            raise AudioValidationError(
                "AUDIO_MISSING_FILENAME",
                "No filename provided with the upload.",
            )
        # Keep only the basename
        name = os.path.basename(filename)
        # Limit length to prevent filesystem issues
        if len(name) > 255:
            name = name[-255:]
        return name

    def _validate_extension(self, filename: str) -> str:
        _, dot_ext = os.path.splitext(filename)
        ext = dot_ext.lstrip(".").lower()
        if ext not in settings.AUDIO_ALLOWED_EXTENSIONS:
            raise AudioValidationError(
                "AUDIO_UNSUPPORTED_FORMAT",
                f"File extension '.{ext}' is not supported. "
                f"Allowed: {settings.AUDIO_ALLOWED_EXTENSIONS}",
            )
        return ext

    def _validate_content_type(self, content_type: str) -> None:
        # Normalise (strip params like '; charset=...')
        ct = content_type.split(";")[0].strip().lower()
        if ct not in settings.AUDIO_ALLOWED_MIME_TYPES:
            raise AudioValidationError(
                "AUDIO_INVALID_CONTENT_TYPE",
                f"Content-Type '{ct}' is not an accepted audio MIME type.",
            )

    @staticmethod
    def _validate_size(data: bytes) -> None:
        max_bytes = settings.AUDIO_MAX_SIZE_MB * 1024 * 1024
        if len(data) > max_bytes:
            raise AudioValidationError(
                "AUDIO_FILE_TOO_LARGE",
                f"File size {len(data)} bytes exceeds maximum "
                f"{settings.AUDIO_MAX_SIZE_MB} MB.",
            )

    @staticmethod
    def _detect_format(data: bytes, declared_ext: str) -> str:
        """
        Inspect magic bytes to confirm the actual file format.

        Returns the detected format string.
        Raises AudioValidationError if the header doesn't match any
        known audio signature.
        """
        header16 = data[:16] if len(data) >= 16 else data

        for fmt, sigs in _MAGIC_SIGNATURES.items():
            for sig in sigs:
                # M4A 'ftyp' box is at offset 4
                offset = 4 if sig == b"ftyp" else 0
                if header16[offset:offset + len(sig)] == sig:
                    return fmt

        # Also accept WAV: bytes 8-11 must be "WAVE"
        if len(data) >= 12 and data[8:12] == b"WAVE":
            return "wav"

        raise AudioValidationError(
            "AUDIO_INVALID_FILE",
            "File header does not match a recognised audio format. "
            "The file may be corrupted or mislabelled.",
        )
