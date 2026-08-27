"""
Explicit Model Download Script.

Downloads the configured pretrained models to the local cache so they are 
available offline during the hackathon.

Usage:
    python -m app.models.download
"""

import sys
import logging
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_downloader")

def download_models():
    """Download models explicitly."""
    logger.info("Starting Phase 4 Model Download...")
    logger.info("This will download approximately 500MB of model weights.")
    
    # 1. NLP Model
    try:
        from transformers import pipeline
        logger.info("Downloading NLP Model: %s", settings.NLP_MODEL_NAME)
        pipeline("text-classification", model=settings.NLP_MODEL_NAME)
        logger.info("NLP Model downloaded successfully.")
    except Exception as e:
        logger.error("Failed to download NLP Model: %s", e)
        sys.exit(1)

    # 2. Embedding Model
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Downloading Embedding Model: %s", settings.EMBEDDING_MODEL_NAME)
        SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        logger.info("Embedding Model downloaded successfully.")
    except Exception as e:
        logger.error("Failed to download Embedding Model: %s", e)
        sys.exit(1)

    # 3. STT Model
    try:
        from transformers import pipeline
        logger.info("Downloading STT Model: %s", settings.STT_MODEL_NAME)
        pipeline("automatic-speech-recognition", model=settings.STT_MODEL_NAME)
        logger.info("STT Model downloaded successfully.")
    except Exception as e:
        logger.error("Failed to download STT Model: %s", e)
        sys.exit(1)

    logger.info("All models downloaded and cached successfully!")
    logger.info("You can now run Aurevia AI Service with AI_MODE=real")

if __name__ == "__main__":
    download_models()
