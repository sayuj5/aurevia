"""
Audio feature extraction.

In DEMO_MODE: computes lightweight features from raw bytes using
only the Python standard library (no librosa / numpy required).

In production: delegates to librosa for full acoustic feature
extraction. Librosa is imported lazily so the service starts without it.

Features computed in DEMO_MODE:
  - RMS (root mean square of signed 16-bit samples for WAV)
  - Zero-crossing rate (estimate from byte transitions)
  - Byte entropy (proxy for signal complexity)

These are NOT clinical/diagnostic features. They are simple signal
statistics used as decision-support indicators.
"""

import math
import struct
from dataclasses import dataclass, field
from typing import Any, Dict

from app.core.config import settings
from app.core.logging import logger


@dataclass
class AudioFeatures:
    """Extracted audio feature set."""
    rms: float
    zero_crossing_rate: float
    is_demo: bool
    additional: Dict[str, Any] = field(default_factory=dict)


class AudioFeatureExtractor:
    """
    Extracts acoustic features from raw audio bytes.

    Design:
      - DEMO_MODE=True  → pure-Python, no external deps
      - DEMO_MODE=False → attempts librosa; falls back to demo on failure
    """

    def extract(self, data: bytes, fmt: str, sample_rate: int = 0) -> AudioFeatures:
        """
        Extract features from audio bytes.

        Args:
            data:        Raw audio file bytes.
            fmt:         Detected format (e.g. "wav").
            sample_rate: Sample rate (from metadata); 0 if unknown.

        Returns:
            AudioFeatures.
        """
        if settings.DEMO_MODE or fmt != "wav":
            return self._demo_features(data)

        # Production path: try librosa
        try:
            return self._librosa_features(data, sample_rate)
        except ImportError:
            logger.warning(
                "librosa not installed — using demo feature extraction."
            )
            return self._demo_features(data)
        except Exception as exc:
            logger.warning(
                "librosa feature extraction failed (%s) — using demo.", exc
            )
            return self._demo_features(data)

    # ------------------------------------------------------------------
    # Demo implementation (stdlib only)
    # ------------------------------------------------------------------

    @staticmethod
    def _demo_features(data: bytes) -> AudioFeatures:
        """
        Compute lightweight proxy features from raw bytes.

        For WAV PCM data, interprets audio payload as 16-bit signed samples.
        For other formats, computes byte-level statistics.
        """
        if not data:
            return AudioFeatures(rms=0.0, zero_crossing_rate=0.0, is_demo=True)

        # Attempt to extract the PCM payload from WAV
        pcm_bytes = _extract_wav_pcm(data)

        if pcm_bytes and len(pcm_bytes) >= 2:
            rms, zcr = _pcm_rms_zcr(pcm_bytes)
        else:
            # Byte-level fallback for non-WAV or unreadable WAV
            rms = _byte_rms(data)
            zcr = _byte_zcr(data)

        # Byte entropy as an additional indicator
        entropy = _byte_entropy(data[:4096])  # sample first 4KB

        additional = {
            "byte_entropy": round(entropy, 4),
            "file_size_bytes": len(data),
            "note": "DEMO_MODE: features are lightweight byte-level statistics.",
        }

        logger.debug("DemoFeatures: rms=%.4f zcr=%.4f entropy=%.4f", rms, zcr, entropy)
        return AudioFeatures(
            rms=round(rms, 6),
            zero_crossing_rate=round(zcr, 6),
            is_demo=True,
            additional=additional,
        )

    # ------------------------------------------------------------------
    # Production implementation (librosa — optional)
    # ------------------------------------------------------------------

    @staticmethod
    def _librosa_features(data: bytes, sample_rate: int) -> AudioFeatures:
        """
        Full acoustic feature extraction using librosa.

        Requires: librosa, soundfile, numpy
        """
        import io
        import numpy as np
        import librosa
        import soundfile as sf

        audio_array, sr = sf.read(io.BytesIO(data))
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)  # mono

        rms_val = float(np.sqrt(np.mean(audio_array ** 2)))
        zcr_val = float(np.mean(librosa.feature.zero_crossing_rate(y=audio_array)))
        mfccs = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
        mfcc_means = [round(float(v), 4) for v in np.mean(mfccs, axis=1)]

        additional: Dict[str, Any] = {
            "mfcc_means": mfcc_means,
            "sample_rate_detected": sr,
        }

        logger.debug("LibrosaFeatures: rms=%.4f zcr=%.4f", rms_val, zcr_val)
        return AudioFeatures(
            rms=round(rms_val, 6),
            zero_crossing_rate=round(zcr_val, 6),
            is_demo=False,
            additional=additional,
        )


# ---------------------------------------------------------------------------
# Helpers for demo feature computation
# ---------------------------------------------------------------------------

def _extract_wav_pcm(data: bytes) -> bytes:
    """Extract the raw PCM payload from a WAV file."""
    try:
        if len(data) < 44 or data[0:4] != b"RIFF" or data[8:12] != b"WAVE":
            return b""
        offset = 12
        while offset < len(data) - 8:
            chunk_id = data[offset:offset + 4]
            chunk_size = struct.unpack_from("<I", data, offset + 4)[0]
            if chunk_id == b"data":
                return data[offset + 8: offset + 8 + chunk_size]
            offset += 8 + chunk_size
    except Exception:
        pass
    return b""


def _pcm_rms_zcr(pcm_bytes: bytes) -> tuple[float, float]:
    """Compute RMS and ZCR from raw 16-bit little-endian PCM samples."""
    n = len(pcm_bytes) // 2
    if n == 0:
        return 0.0, 0.0

    samples = struct.unpack_from(f"<{n}h", pcm_bytes[:n * 2])

    # RMS normalised to [-1, 1]
    scale = 32768.0
    rms = math.sqrt(sum((s / scale) ** 2 for s in samples) / n)

    # Zero crossings
    crossings = sum(
        1 for i in range(1, len(samples))
        if (samples[i] >= 0) != (samples[i - 1] >= 0)
    )
    zcr = crossings / (len(samples) - 1) if len(samples) > 1 else 0.0

    return rms, zcr


def _byte_rms(data: bytes) -> float:
    """Byte-level RMS as a proxy for amplitude."""
    if not data:
        return 0.0
    sample = data[:4096]
    mean_sq = sum(b ** 2 for b in sample) / len(sample)
    return math.sqrt(mean_sq) / 255.0


def _byte_zcr(data: bytes) -> float:
    """Byte-level zero-crossing proxy."""
    sample = data[:4096]
    if len(sample) < 2:
        return 0.0
    mid = 128
    crossings = sum(
        1 for i in range(1, len(sample))
        if (sample[i] >= mid) != (sample[i - 1] >= mid)
    )
    return crossings / (len(sample) - 1)


def _byte_entropy(data: bytes) -> float:
    """Shannon entropy of byte frequencies."""
    if not data:
        return 0.0
    freq: Dict[int, int] = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    total = len(data)
    entropy = -sum((c / total) * math.log2(c / total) for c in freq.values())
    return entropy
