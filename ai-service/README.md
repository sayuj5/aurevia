# Aurevia AI Intelligence Service

This directory contains the AI Intelligence Layer of the Aurevia project.

## Overview
The AI service is built with Python 3.12+ and FastAPI. It provides endpoints for NLP text analysis, audio feature extraction, machine learning risk prediction, and RAG capabilities.

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup configuration:
   ```bash
   cp .env.example .env
   ```

## 🚀 Running the Service

The AI Service supports two execution modes:

### 1. DEMO MODE (Default)
Fast, lightweight, and requires no large AI model downloads. Perfect for rapid UI development and testing.

```bash
uvicorn app.main:app --reload
```

### 2. REAL AI MODE (Phase 4)
Runs actual pretrained ML models (DistilBERT, MiniLM, Whisper).

First, explicitly download the models to your local cache (~500MB):
```bash
python -m app.models.download
```

Then configure `.env` to use the real models:
```env
AI_MODE=real
AI_DEVICE=cpu
```

Finally, start the server:
```bash
uvicorn app.main:app --reload
```

## 🧪 Testing
Run tests using pytest:
```bash
pytest tests/
```

## Docker
Build and run with Docker:
```bash
docker build -t aurevia-ai-service .
docker run -p 8000:8000 --env-file .env aurevia-ai-service
```
