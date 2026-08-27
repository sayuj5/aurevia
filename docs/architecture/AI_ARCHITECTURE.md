# Aurevia AI Architecture

## System Architecture

```text
                    Aurevia AI
                         │
          ┌──────────────┴──────────────┐
          ↓                             ↓
       TEXT PIPELINE                AUDIO PIPELINE
          │                             │
     Preprocessing                Audio Validation & Storage
          │                             │
     NLP Model (Sentiment)        Audio Features & STT
          │                             │
     Embeddings (Semantic)        Transcription
          │                             │
          └──────────────┬──────────────┘
                         ↓
                  AI Intelligence (Phase 4 Orchestration)
                         │
                         ↓
                 Structured Output
```

## Overview
The Aurevia AI Service is a microservice designed to support human reviewers by providing AI-assisted decision-support metrics based on textual, auditory, structured, and historical data.

## Key Technologies
- **Framework**: FastAPI (Python 3.12+)
- **ML/AI**: PyTorch, Hugging Face Transformers, Sentence Transformers, scikit-learn, XGBoost, Librosa, OpenSMILE
- **Database**: PostgreSQL (via SQLAlchemy/Alembic) with TimescaleDB and pgvector
- **Messaging**: RabbitMQ / Celery (for async tasks)
- **Storage**: MinIO / S3
- **Local LLM**: Ollama

## Modules
- `nlp/`: Processes text using Transformers.
- `audio/`: Extracts features using Librosa and OpenSMILE.
- `ml/`: Predicts risk scores using XGBoost and SHAP explainability.
- `risk/`: Calculates explainable, combined decision-support scores.
- `rag/`: Manages knowledge ingestion, embedding, and retrieval.
- `storage/`: Interfaces with PostgreSQL, pgvector, and MinIO.

*(More detailed architecture diagrams and documentation will be added as phases progress)*

---

### Phase 3: Audio AI & Storage Foundation
Completed. Modular audio-processing pipeline supporting:
1. Validation (MIME, Magic-Bytes).
2. Object Storage (`LocalObjectStorage`, `MinIOObjectStorage`).
3. Audio Metadata & Feature extraction.

### Phase 4: Real AI/ML Model Integration
Completed. Integrated actual pretrained models via Hugging Face and SentenceTransformers:
1. **Model Manager (`app/models/manager.py`)**: Thread-safe lazy-loading of models to conserve RAM on startup.
2. **NLP Model**: `distilbert-base-uncased-finetuned-sst-2-english` (Binary Sentiment Analysis).
3. **Embedding Model**: `all-MiniLM-L6-v2` (384-dimension Semantic Embeddings).
4. **Speech-to-Text**: `openai/whisper-tiny` (Multilingual Transcription).
5. **AI Orchestration**: Orchestrates text and audio processing based on configuration (`AI_MODE=real` vs `AI_MODE=demo`).

All models run offline and on CPU by default. No training datasets are required. Models must be explicitly downloaded using `python -m app.models.download`.

### Phase 5+: Advanced Analytics & RAG
*(Planned)* - Context-aware analysis, Vector DB integration, and advanced risk scoring.

---

## NLP Pipeline (Phase 2)

```
POST /api/v1/nlp/analyze
        ↓
   Validation (Pydantic schema)
        ↓
   Length check (10 000 char limit)
        ↓
   Text Preprocessing
     - Unicode NFC normalization
     - Control character removal
     - Whitespace normalization
     - Metrics (chars, words, sentences)
        ↓
   Tokenization   (SimpleTokenizer — replaceable)
        ↓
   Language Detection  (HeuristicLanguageDetector — replaceable)
        ↓
   NLP Model  (DemoNLPModel → future transformer)
        ↓
   Embedding  (DemoEmbeddingProvider → future SentenceTransformer)
        ↓
   NLPAnalyzeResponse (Pydantic)
```

### DEMO_MODE
When `DEMO_MODE=true` (default), the pipeline runs entirely with built-in
lightweight implementations — no downloads, no GPU, no API keys required.

---

## Audio Pipeline (Phase 3)

```
POST /api/v1/audio/analyze (multipart/form-data)
        ↓
   AudioFileValidator
     - Sanitises filename
     - Checks allowed extensions & MIME types
     - Size limit check (default 50MB)
     - Magic bytes verification
        ↓
   BaseObjectStorage
     - LocalObjectStorage (DEMO_MODE / default)
     - MinIOObjectStorage (Production)
        ↓
   AudioMetadataExtractor
     - Natively parses WAV RIFF headers
     - Returns placeholders for other formats in demo mode
        ↓
   AudioFeatureExtractor
     - DEMO: pure-Python byte-level statistics (RMS, ZCR, entropy)
     - PROD: lazily loads librosa/soundfile for acoustic features
        ↓
   BaseTranscriptionProvider (Stub)
     - Interface ready for Whisper / Google STT in later phases
        ↓
   AudioAnalyzeResponse (Pydantic)
```

### Security & Path Traversal
- Raw filenames from uploads are **never** used to construct internal paths.
- Paths are generated via UUIDs.
- `LocalObjectStorage` forcibly resolves paths and guarantees they do not escape the configured base directory.
