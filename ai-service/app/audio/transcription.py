"""
Transcription abstraction.

Defines the interface for speech-to-text providers.
Phase 3 provides only the interface and a demo stub.

A real implementation (Whisper, Google STT, etc.) can be introduced
in a later phase without changing the public API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.core.logging import logger


@dataclass
class TranscriptionResult:
    """Result from a transcription provider."""
    available: bool
    text: Optional[str]
    provider: Optional[str]


class BaseTranscriptionProvider(ABC):
    """Abstract interface for speech-to-text providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def transcribe(self, data: bytes, fmt: str, sample_rate: int) -> TranscriptionResult:
        """
        Transcribe audio bytes to text.

        Args:
            data:        Raw audio bytes.
            fmt:         Audio format string.
            sample_rate: Sample rate in Hz.

        Returns:
            TranscriptionResult.
        """
        ...


class DemoTranscriptionProvider(BaseTranscriptionProvider):
    """
    Demo/placeholder transcription provider.

    Always returns available=False indicating transcription is not
    yet implemented. This allows the API to include the transcription
    field without blocking Phase 3.
    """

    @property
    def name(self) -> str:
        return "demo-transcription-stub"

    def transcribe(self, data: bytes, fmt: str, sample_rate: int) -> TranscriptionResult:
        logger.debug("DemoTranscriptionProvider: transcription not available in Phase 3")
        return TranscriptionResult(
            available=False,
            text=None,
            provider=self.name,
        )


class WhisperTranscriptionProvider(BaseTranscriptionProvider):
    """
    Real Transcription Provider using Whisper via Hugging Face Transformers.
    Loads lazily via the global model_manager.
    """

    def __init__(self, model_name: str, device: str = "cpu") -> None:
        self._model_name = model_name
        self._device_str = device

        def _load_whisper():
            try:
                import torch
                from transformers import pipeline
            except ImportError:
                raise RuntimeError("Missing required dependencies for real transcription (transformers, torch).")

            device_id = -1
            if self._device_str.lower() in ("cuda", "gpu") and torch.cuda.is_available():
                device_id = 0
            
            logger.info("Initializing Whisper pipeline: %s on device %s", self._model_name, device_id)
            return pipeline(
                "automatic-speech-recognition",
                model=self._model_name,
                device=device_id
            )

        from app.models.manager import model_manager
        model_manager.register_loader(f"stt_{self._model_name}", _load_whisper)

    @property
    def name(self) -> str:
        return f"whisper/{self._model_name}"

    def transcribe(self, data: bytes, fmt: str, sample_rate: int) -> TranscriptionResult:
        from app.models.manager import model_manager
        
        try:
            pipe = model_manager.get_model(f"stt_{self._model_name}")
            
            # The pipeline accepts raw bytes directly if it can decode them (it uses soundfile/ffmpeg under the hood).
            # Because we might not have ffmpeg installed, it's safer to pass a numpy array. 
            # We already use soundfile in features if it's installed, let's use it here.
            import io
            import numpy as np
            try:
                import soundfile as sf
            except ImportError:
                raise RuntimeError("soundfile is required for transcription. Please install it.")

            audio_array, sr = sf.read(io.BytesIO(data))
            
            # Whisper expects 16kHz audio. If sr != 16000, we should ideally resample.
            # But the HF pipeline often handles this via its feature extractor automatically if provided as dict:
            inputs = {"sampling_rate": sr, "raw": audio_array}
            
            outputs = pipe(inputs, generate_kwargs={"task": "transcribe"})
            
            text = outputs.get("text", "").strip()
            
            return TranscriptionResult(
                available=True,
                text=text,
                provider=self.name,
            )
        except Exception as exc:
            logger.error("Whisper transcription failed: %s", exc)
            return TranscriptionResult(
                available=False,
                text=None,
                provider=self.name,
            )


_default_provider: BaseTranscriptionProvider = DemoTranscriptionProvider()


def get_transcription_provider() -> BaseTranscriptionProvider:
    """Return the active transcription provider."""
    return _default_provider
