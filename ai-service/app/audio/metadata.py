"""
Audio metadata extraction.

Reads basic audio properties (duration, sample rate, channels)
from raw bytes without requiring heavy external libraries in DEMO_MODE.

WAV metadata is parsed from the RIFF/WAVE header (pure Python).
For other formats, DEMO_MODE returns safe placeholder values.

In production, replace/extend with soundfile or librosa.
"""

import struct
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import logger


@dataclass
class AudioMetadata:
    """Basic audio properties extracted from the file."""
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str


class AudioMetadataExtractor:
    """
    Extracts audio metadata from raw bytes.

    WAV files are parsed natively.
    All other formats return demo placeholders in DEMO_MODE.
    """

    def extract(self, data: bytes, fmt: str) -> AudioMetadata:
        """
        Extract metadata from audio bytes.

        Args:
            data: Raw audio file bytes (already validated).
            fmt:  Detected format string (e.g. "wav", "mp3").

        Returns:
            AudioMetadata.
        """
        if fmt == "wav":
            try:
                return self._parse_wav(data)
            except Exception as exc:
                logger.warning("WAV header parse failed: %s — using demo values", exc)

        # Fallback: demo placeholder values
        return self._demo_metadata(fmt)

    # ------------------------------------------------------------------
    # WAV header parser (pure Python, no deps)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_wav(data: bytes) -> AudioMetadata:
        """
        Parse the RIFF/WAVE header to extract sample rate, channels,
        bits-per-sample, and duration.

        WAV structure:
          Offset  Size  Field
          0       4     "RIFF"
          4       4     ChunkSize (LE uint32)
          8       4     "WAVE"
          12      4     "fmt "
          16      4     SubChunk1Size (16 for PCM)
          20      2     AudioFormat (1 = PCM)
          22      2     NumChannels
          24      4     SampleRate
          28      4     ByteRate
          32      2     BlockAlign
          34      2     BitsPerSample
          36      4     "data"
          40      4     SubChunk2Size
        """
        if len(data) < 44:
            raise ValueError("File too short to be a valid WAV")

        if data[0:4] != b"RIFF" or data[8:12] != b"WAVE":
            raise ValueError("Not a RIFF/WAVE file")

        # Parse fmt chunk (assumes standard 16-byte PCM fmt)
        # NumChannels at offset 22
        num_channels = struct.unpack_from("<H", data, 22)[0]
        # SampleRate at offset 24
        sample_rate = struct.unpack_from("<I", data, 24)[0]
        # BitsPerSample at offset 34
        bits_per_sample = struct.unpack_from("<H", data, 34)[0]

        # Find the data chunk (search past fmt chunk)
        data_chunk_size = 0
        offset = 36
        while offset < len(data) - 8:
            chunk_id = data[offset:offset + 4]
            chunk_size = struct.unpack_from("<I", data, offset + 4)[0]
            if chunk_id == b"data":
                data_chunk_size = chunk_size
                break
            offset += 8 + chunk_size

        # Duration = data_size / (sample_rate * channels * bytes_per_sample)
        bytes_per_sample = max(1, bits_per_sample // 8)
        denom = sample_rate * num_channels * bytes_per_sample
        duration = data_chunk_size / denom if denom > 0 else 0.0

        logger.debug(
            "WAV metadata: channels=%d sr=%d bits=%d duration=%.2fs",
            num_channels, sample_rate, bits_per_sample, duration,
        )

        return AudioMetadata(
            duration_seconds=round(duration, 3),
            sample_rate=sample_rate,
            channels=num_channels,
            format="wav",
        )

    @staticmethod
    def _demo_metadata(fmt: str) -> AudioMetadata:
        """Return safe demo placeholder metadata for non-WAV formats."""
        logger.debug("AudioMetadata: using demo values for format=%s", fmt)
        return AudioMetadata(
            duration_seconds=0.0,
            sample_rate=0,
            channels=0,
            format=fmt,
        )
