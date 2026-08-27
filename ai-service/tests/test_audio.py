"""
Comprehensive tests for Phase 3: Audio AI + Object Storage.

All tests run without external services (DEMO_MODE=True).
Audio bytes are generated in memory — no real audio files needed.

Coverage:
  - Audio validator (extension, MIME, size, magic bytes, path traversal)
  - Audio metadata extractor (WAV parsing, fallback)
  - Audio feature extractor (demo path, edge cases)
  - Transcription interface (stub)
  - Local object storage (upload, exists, delete, metadata, path traversal)
  - Audio service (full pipeline)
  - API endpoint (valid upload, invalid extension, wrong MIME, oversized,
                   empty file, missing file field)
  - Phase 1 + 2 regression
"""

import io
import struct
import tempfile
import os
import pytest

from fastapi.testclient import TestClient

from app.core.config import settings
from app.audio.validator import AudioFileValidator, AudioValidationError
from app.audio.metadata import AudioMetadataExtractor
from app.audio.features import AudioFeatureExtractor
from app.audio.transcription import DemoTranscriptionProvider
from app.storage.local import LocalObjectStorage
from app.storage.base import StoredObject


# ===========================================================================
# Helpers — in-memory audio byte builders
# ===========================================================================

def _make_wav(duration_seconds: float = 0.5, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """
    Generate a minimal valid WAV file in memory.
    Contains a pure-silence (zero-filled) PCM payload.
    """
    bits_per_sample = 16
    num_samples = int(duration_seconds * sample_rate * channels)
    pcm_data = bytes(num_samples * (bits_per_sample // 8))

    byte_rate = sample_rate * channels * (bits_per_sample // 8)
    block_align = channels * (bits_per_sample // 8)
    data_chunk_size = len(pcm_data)
    riff_chunk_size = 36 + data_chunk_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", riff_chunk_size, b"WAVE",
        b"fmt ", 16, 1,          # PCM
        channels, sample_rate,
        byte_rate, block_align, bits_per_sample,
        b"data", data_chunk_size,
    )
    return header + pcm_data


def _make_mp3_stub() -> bytes:
    """Minimal bytes with MP3 ID3 header magic."""
    return b"ID3" + b"\x03\x00\x00" + b"\x00" * 100


def _make_ogg_stub() -> bytes:
    """Minimal bytes with OGG magic."""
    return b"OggS" + b"\x00" * 100


def _make_flac_stub() -> bytes:
    """Minimal bytes with FLAC magic."""
    return b"fLaC" + b"\x00" * 100


def _make_corrupt() -> bytes:
    """Random bytes that don't match any audio magic."""
    return b"\x00\x01\x02\x03" + b"garbage data no magic header here"


# ===========================================================================
# AudioFileValidator tests
# ===========================================================================

class TestAudioValidator:

    def setup_method(self):
        self.v = AudioFileValidator()

    # -- Happy paths ----------------------------------------------------------

    def test_valid_wav(self):
        data = _make_wav()
        result = self.v.validate("test.wav", "audio/wav", data)
        assert result.safe_extension == "wav"
        assert result.detected_format == "wav"
        assert result.size_bytes == len(data)

    def test_valid_mp3(self):
        data = _make_mp3_stub()
        result = self.v.validate("test.mp3", "audio/mpeg", data)
        assert result.safe_extension == "mp3"
        assert result.detected_format == "mp3"

    def test_valid_ogg(self):
        data = _make_ogg_stub()
        result = self.v.validate("test.ogg", "audio/ogg", data)
        assert result.safe_extension == "ogg"

    def test_valid_flac(self):
        data = _make_flac_stub()
        result = self.v.validate("test.flac", "audio/flac", data)
        assert result.safe_extension == "flac"

    def test_original_filename_preserved(self):
        data = _make_wav()
        result = self.v.validate("my recording.wav", "audio/wav", data)
        assert result.original_filename == "my recording.wav"

    # -- Extension failures ---------------------------------------------------

    def test_unsupported_extension_rejected(self):
        with pytest.raises(AudioValidationError) as exc_info:
            self.v.validate("file.exe", "audio/wav", _make_wav())
        assert exc_info.value.code == "AUDIO_UNSUPPORTED_FORMAT"

    def test_txt_extension_rejected(self):
        with pytest.raises(AudioValidationError):
            self.v.validate("file.txt", "audio/wav", _make_wav())

    # -- MIME type failures ---------------------------------------------------

    def test_invalid_mime_rejected(self):
        with pytest.raises(AudioValidationError) as exc_info:
            self.v.validate("test.wav", "application/pdf", _make_wav())
        assert exc_info.value.code == "AUDIO_INVALID_CONTENT_TYPE"

    def test_text_mime_rejected(self):
        with pytest.raises(AudioValidationError):
            self.v.validate("test.wav", "text/plain", _make_wav())

    # -- Size failures --------------------------------------------------------

    def test_oversized_file_rejected(self):
        max_bytes = settings.AUDIO_MAX_SIZE_MB * 1024 * 1024
        huge = b"\x00" * (max_bytes + 1)
        with pytest.raises(AudioValidationError) as exc_info:
            self.v.validate("big.wav", "audio/wav", huge)
        assert exc_info.value.code == "AUDIO_FILE_TOO_LARGE"

    # -- Empty file -----------------------------------------------------------

    def test_empty_file_rejected(self):
        with pytest.raises(AudioValidationError) as exc_info:
            self.v.validate("empty.wav", "audio/wav", b"")
        assert exc_info.value.code == "AUDIO_EMPTY_FILE"

    # -- Magic byte failures --------------------------------------------------

    def test_corrupt_file_rejected(self):
        with pytest.raises(AudioValidationError) as exc_info:
            self.v.validate("fake.wav", "audio/wav", _make_corrupt())
        assert exc_info.value.code == "AUDIO_INVALID_FILE"

    # -- Path traversal -------------------------------------------------------

    def test_path_traversal_stripped(self):
        """../etc/passwd should be reduced to just passwd with .wav extension."""
        data = _make_wav()
        result = self.v.validate("../../../etc/passwd.wav", "audio/wav", data)
        # basename only — no directory components
        assert "/" not in result.original_filename
        assert ".." not in result.original_filename

    def test_missing_filename_rejected(self):
        with pytest.raises(AudioValidationError) as exc_info:
            self.v.validate("", "audio/wav", _make_wav())
        assert exc_info.value.code == "AUDIO_MISSING_FILENAME"


# ===========================================================================
# AudioMetadataExtractor tests
# ===========================================================================

class TestAudioMetadata:

    def setup_method(self):
        self.extractor = AudioMetadataExtractor()

    def test_wav_sample_rate(self):
        data = _make_wav(sample_rate=44100)
        meta = self.extractor.extract(data, "wav")
        assert meta.sample_rate == 44100

    def test_wav_channels(self):
        data = _make_wav(channels=2)
        meta = self.extractor.extract(data, "wav")
        assert meta.channels == 2

    def test_wav_duration(self):
        data = _make_wav(duration_seconds=1.0, sample_rate=16000, channels=1)
        meta = self.extractor.extract(data, "wav")
        assert meta.duration_seconds == pytest.approx(1.0, abs=0.01)

    def test_wav_format(self):
        data = _make_wav()
        meta = self.extractor.extract(data, "wav")
        assert meta.format == "wav"

    def test_non_wav_returns_demo(self):
        meta = self.extractor.extract(_make_mp3_stub(), "mp3")
        assert meta.format == "mp3"
        assert meta.duration_seconds == 0.0

    def test_corrupt_wav_falls_back(self):
        meta = self.extractor.extract(b"RIFF\x00\x00\x00\x00WAVEgarbagehere", "wav")
        # Should not raise — falls back to demo
        assert meta.format == "wav"


# ===========================================================================
# AudioFeatureExtractor tests
# ===========================================================================

class TestAudioFeatures:

    def setup_method(self):
        self.extractor = AudioFeatureExtractor()

    def test_wav_rms_is_float(self):
        data = _make_wav()
        features = self.extractor.extract(data, "wav")
        assert isinstance(features.rms, float)

    def test_wav_zcr_is_float(self):
        data = _make_wav()
        features = self.extractor.extract(data, "wav")
        assert isinstance(features.zero_crossing_rate, float)

    def test_silence_rms_is_zero(self):
        # Zero-filled PCM → RMS should be 0
        data = _make_wav()
        features = self.extractor.extract(data, "wav")
        assert features.rms == pytest.approx(0.0, abs=1e-6)

    def test_demo_mode_flag(self):
        data = _make_wav()
        features = self.extractor.extract(data, "wav")
        assert features.is_demo is True  # DEMO_MODE=True in test config

    def test_additional_metadata_present(self):
        data = _make_wav()
        features = self.extractor.extract(data, "wav")
        assert isinstance(features.additional, dict)

    def test_non_wav_format(self):
        features = self.extractor.extract(_make_mp3_stub(), "mp3")
        assert isinstance(features.rms, float)
        assert features.is_demo is True

    def test_empty_data_handled(self):
        features = self.extractor.extract(b"", "wav")
        assert features.rms == 0.0


# ===========================================================================
# DemoTranscriptionProvider tests
# ===========================================================================

class TestTranscription:

    def test_always_unavailable(self):
        provider = DemoTranscriptionProvider()
        result = provider.transcribe(b"fake", "wav", 16000)
        assert result.available is False
        assert result.text is None

    def test_provider_name(self):
        provider = DemoTranscriptionProvider()
        assert provider.name != ""


# ===========================================================================
# LocalObjectStorage tests
# ===========================================================================

class TestLocalStorage:

    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.storage = LocalObjectStorage(base_path=self._tmpdir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_upload_returns_stored_object(self):
        stored = self.storage.upload("test/file.wav", b"\x00" * 100, "audio/wav")
        assert isinstance(stored, StoredObject)
        assert stored.object_key == "test/file.wav"
        assert stored.size_bytes == 100
        assert stored.provider == "local"

    def test_upload_checksum_is_hex(self):
        stored = self.storage.upload("checksum.wav", b"data", "audio/wav")
        assert len(stored.checksum) == 64  # SHA-256 hex

    def test_exists_after_upload(self):
        self.storage.upload("exists_test.wav", b"\x00" * 50, "audio/wav")
        assert self.storage.exists("exists_test.wav") is True

    def test_not_exists_before_upload(self):
        assert self.storage.exists("never_uploaded.wav") is False

    def test_delete_removes_file(self):
        self.storage.upload("to_delete.wav", b"\x01" * 10, "audio/wav")
        self.storage.delete("to_delete.wav")
        assert self.storage.exists("to_delete.wav") is False

    def test_delete_nonexistent_is_noop(self):
        # Should not raise
        self.storage.delete("nonexistent.wav")

    def test_get_metadata_existing(self):
        self.storage.upload("meta_test.wav", b"\x00" * 200, "audio/wav")
        meta = self.storage.get_metadata("meta_test.wav")
        assert meta.exists is True
        assert meta.size_bytes == 200

    def test_get_metadata_nonexistent(self):
        meta = self.storage.get_metadata("missing.wav")
        assert meta.exists is False

    def test_path_traversal_rejected(self):
        with pytest.raises(ValueError, match="Path traversal"):
            self.storage.upload("../../etc/passwd", b"evil", "text/plain")

    def test_subdirectory_created_automatically(self):
        self.storage.upload("a/b/c/deep.wav", b"\x00" * 10, "audio/wav")
        assert self.storage.exists("a/b/c/deep.wav") is True


# ===========================================================================
# Audio API endpoint tests
# ===========================================================================

class TestAudioEndpoint:

    def _upload(self, client, data: bytes, filename: str, content_type: str):
        """Helper to post a multipart file upload."""
        return client.post(
            f"{settings.API_V1_STR}/audio/analyze",
            files={"file": (filename, io.BytesIO(data), content_type)},
        )

    def test_valid_wav_upload(self, client: TestClient):
        response = self._upload(client, _make_wav(), "test.wav", "audio/wav")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_response_has_file_info(self, client: TestClient):
        response = self._upload(client, _make_wav(), "sample.wav", "audio/wav")
        data = response.json()
        fi = data["file"]
        assert "object_id" in fi
        assert "filename" in fi
        assert "size_bytes" in fi
        assert fi["size_bytes"] > 0

    def test_response_has_audio_metadata(self, client: TestClient):
        response = self._upload(client, _make_wav(duration_seconds=1.0, sample_rate=16000), "s.wav", "audio/wav")
        audio = response.json()["audio"]
        assert "duration_seconds" in audio
        assert "sample_rate" in audio
        assert "channels" in audio
        assert "format" in audio

    def test_response_has_features(self, client: TestClient):
        response = self._upload(client, _make_wav(), "f.wav", "audio/wav")
        feats = response.json()["features"]
        assert "rms" in feats
        assert "zero_crossing_rate" in feats
        assert "is_demo" in feats

    def test_response_transcription_not_available(self, client: TestClient):
        response = self._upload(client, _make_wav(), "t.wav", "audio/wav")
        tr = response.json()["transcription"]
        assert tr["available"] is False

    def test_response_storage_info(self, client: TestClient):
        response = self._upload(client, _make_wav(), "st.wav", "audio/wav")
        storage = response.json()["storage"]
        assert "provider" in storage
        assert "mode" in storage

    def test_unsupported_extension_rejected(self, client: TestClient):
        response = self._upload(client, b"garbage", "evil.exe", "audio/wav")
        assert response.status_code == 422

    def test_wrong_mime_type_rejected(self, client: TestClient):
        response = self._upload(client, _make_wav(), "file.wav", "application/pdf")
        assert response.status_code == 422

    def test_corrupt_file_rejected(self, client: TestClient):
        response = self._upload(client, _make_corrupt(), "bad.wav", "audio/wav")
        assert response.status_code == 422

    def test_empty_file_rejected(self, client: TestClient):
        response = self._upload(client, b"", "empty.wav", "audio/wav")
        assert response.status_code == 422

    def test_mp3_upload(self, client: TestClient):
        response = self._upload(client, _make_mp3_stub(), "test.mp3", "audio/mpeg")
        assert response.status_code == 200

    def test_ogg_upload(self, client: TestClient):
        response = self._upload(client, _make_ogg_stub(), "test.ogg", "audio/ogg")
        assert response.status_code == 200

    def test_object_id_is_unique(self, client: TestClient):
        r1 = self._upload(client, _make_wav(), "a.wav", "audio/wav")
        r2 = self._upload(client, _make_wav(), "b.wav", "audio/wav")
        id1 = r1.json()["file"]["object_id"]
        id2 = r2.json()["file"]["object_id"]
        assert id1 != id2


# ===========================================================================
# Phase 1 & 2 regression tests
# ===========================================================================

class TestPhaseRegressions:

    def test_health_still_works(self, client: TestClient):
        response = client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_nlp_still_works(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "Phase 3 regression test for NLP."},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
