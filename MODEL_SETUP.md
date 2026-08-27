# Model Setup

The Aurevia AI Service (`ai-service/`) supports both a lightweight development mode and a fully functional AI mode using state-of-the-art models.

## AI Execution Modes

### 1. Demo Mode (Default)
Fast, lightweight, and requires no large AI model downloads. This is perfect for rapid UI development, backend integration testing, and running on standard hardware without GPU acceleration. It simulates AI responses and risk assessments.

### 2. Real AI Mode
Runs actual pretrained ML models for NLP and audio processing. This requires initial model downloads and uses more system memory and compute resources.

## Implemented Models

The following models are supported and configured in the repository:

### `distilbert-base-uncased-finetuned-sst-2-english`
- **Purpose**: Sentiment analysis and text-based distress evaluation.
- **Provider/Library**: Hugging Face `transformers`.
- **Expected Usage**: Analyzing journal entries and chat messages for negative sentiment and distress signals.

### `sentence-transformers/all-MiniLM-L6-v2`
- **Purpose**: Text embeddings and semantic similarity.
- **Provider/Library**: Hugging Face `sentence-transformers`.
- **Expected Usage**: Generating dense vector representations of text for retrieval-augmented generation (RAG) capabilities.

### `openai/whisper-tiny`
- **Purpose**: Audio transcription and processing.
- **Provider/Library**: Hugging Face `transformers` / OpenAI.
- **Expected Usage**: Converting user audio inputs (where supported) into text for downstream NLP analysis.

## Setup Requirements

### Downloading Models
To explicitly download the models to your local cache (approximately 500MB total), run the included utility script:

```bash
cd ai-service
python -m app.models.download
```

> **Warning:** Never commit model weights or Hugging Face cache directories to the repository. The `.gitignore` in `ai-service/` ensures these remain excluded.

### Configuration
To activate Real AI Mode, update your `ai-service/.env` file:

```env
AI_MODE=real
# Set to 'cuda' or 'mps' if a compatible GPU is available, otherwise 'cpu'
AI_DEVICE=cpu 
```

### CPU / GPU Considerations
- **CPU**: All models are chosen to be relatively lightweight (e.g., `MiniLM`, `whisper-tiny`) to allow reasonable inference speeds on standard CPUs.
- **GPU**: If available (NVIDIA CUDA or Apple Silicon MPS), PyTorch will utilize the hardware for significantly faster inference. Set `AI_DEVICE` accordingly.

### Caching Considerations
Models are cached locally by Hugging Face (typically in `~/.cache/huggingface/hub`). Ensure you have adequate disk space. The AI service loads models into memory on startup; monitor RAM usage (expect ~1-2GB peak memory usage during initialization).

### Troubleshooting
- **Memory Errors**: If the service crashes on startup, verify sufficient RAM is available. Fall back to `AI_MODE=demo` if necessary.
- **Download Failures**: Ensure a stable internet connection when running the download script. You can clear the Hugging Face cache if a download is corrupted.
