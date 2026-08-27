# Aurevia AI API Contract

Base URL: `/api/v1`

## Health Check
- **Endpoint**: `GET /health`
- **Description**: Returns the health status of the AI service.
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "Aurevia AI Service",
    "version": "0.1.0",
    "timestamp": "2024-05-18T12:00:00.000Z"
  }
  ```

*(To be expanded in future phases for Audio, ML, Risk, and RAG endpoints)*

---

## NLP Analysis
- **Endpoint**: `POST /api/v1/nlp/analyze`
- **Description**: Runs the full NLP pipeline on submitted text.
- **Request**:
  ```json
  { "text": "Example text for Aurevia NLP analysis." }
  ```
- **Response** (200 OK):
  ```json
  {
    "success": true,
    "language": { "code": "en", "name": "English", "confidence": 0.5 },
    "preprocessing": { "character_count": 38, "word_count": 6, "sentence_count": 1 },
    "tokens": { "count": 7, "items": ["Example", "text", ...] },
    "model": { "name": "aurevia-demo-nlp", "version": "0.1.0-demo", "mode": "demo" },
    "embedding": { "provider": "aurevia-demo-embeddings", "dimensions": 64, "is_demo": true }
  }
  ```
- **Validation Errors** (422): empty text, whitespace-only, missing field, text > 10 000 chars.
- **DEMO_MODE**: All steps complete without any external AI services or model downloads.
- **Privacy**: Raw text is never logged or persisted.

---

## Audio Analysis
- **Endpoint**: `POST /api/v1/audio/analyze`
- **Content-Type**: `multipart/form-data`
- **Description**: Uploads an audio file, stores it, and extracts metadata and features.
- **Request**:
  Form field `file` containing the audio upload (WAV, MP3, OGG, M4A, FLAC).
- **Response** (200 OK):
  ```json
  {
    "success": true,
    "file": {
      "object_id": "audio/2026/08/25/a1b2c3d4.wav",
      "filename": "original_recording.wav",
      "content_type": "audio/wav",
      "size_bytes": 1048576
    },
    "audio": {
      "duration_seconds": 32.5,
      "sample_rate": 16000,
      "channels": 1,
      "format": "wav"
    },
    "features": {
      "rms": 0.0452,
      "zero_crossing_rate": 0.12,
      "is_demo": true,
      "additional": { "byte_entropy": 7.91 }
    },
    "transcription": {
      "available": false,
      "text": null,
      "provider": "demo-transcription-stub"
    },
    "storage": {
      "provider": "local",
      "mode": "demo",
      "object_key": "audio/2026/08/25/a1b2c3d4.wav"
    }
  }
  ```
- **Validation Errors** (422): invalid extension, invalid MIME type, missing file, empty file, failed magic-bytes check.
- **Size Errors** (413/422): file exceeds 50MB limit.
- **DEMO_MODE**: Runs pure-Python WAV parsing and byte statistics; local disk storage.
