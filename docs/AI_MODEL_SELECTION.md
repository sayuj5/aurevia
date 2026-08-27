# AI Model Selection

This document outlines the pretrained models selected for Phase 4 of Aurevia's Intelligence Layer.

## 1. NLP Model: Sentiment Analysis
- **Task:** Binary Sentiment Analysis (Positive/Negative)
- **Model:** `distilbert-base-uncased-finetuned-sst-2-english` (Hugging Face)
- **Size:** ~268 MB
- **RAM Requirement:** ~500 MB
- **CPU Feasibility:** Excellent.
- **Why Selected:** DistilBERT is a lightweight version of BERT, offering near-SOTA accuracy with a 40% smaller footprint and 60% faster inference on CPU. This avoids heavy memory loads.
- **Alternatives:** `cardiffnlp/twitter-roberta-base-sentiment` (larger, slower).
- **Dataset:** None required (pretrained inference only).
- **License:** Apache 2.0.

## 2. Embedding Model
- **Task:** Semantic Vector Generation (384 dimensions)
- **Model:** `all-MiniLM-L6-v2` (SentenceTransformers)
- **Size:** ~91 MB
- **RAM Requirement:** ~300 MB
- **CPU Feasibility:** Outstanding.
- **Why Selected:** It is the gold standard for lightweight, efficient embeddings for search and semantic similarity.
- **Alternatives:** `bge-small-en-v1.5` (slightly larger).
- **Dataset:** None required (pretrained inference only).
- **License:** Apache 2.0.

## 3. Speech-to-Text Model
- **Task:** Audio Transcription
- **Model:** `openai/whisper-tiny` (Hugging Face)
- **Size:** ~151 MB
- **RAM Requirement:** ~1 GB
- **CPU Feasibility:** Great. The 39M parameter size is optimized for CPU execution.
- **Why Selected:** Robust multilingual transcription. Using Hugging Face's pipeline avoids complex global dependencies like `ffmpeg`.
- **Alternatives:** `openai/whisper-base` (~290 MB, slower), `Vosk`.
- **Dataset:** None required (pretrained inference only).
- **License:** MIT.

## Requirements
No custom datasets are created or downloaded. All models are cached offline.
To pre-download the models for the hackathon without running the app:
```bash
python -m app.models.download
```
