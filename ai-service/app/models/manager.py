import threading
from typing import Any, Dict

class ModelManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._models: Dict[str, Any] = {}
        return cls._instance

    def get_nlp_pipeline(self):
        with self._lock:
            if "nlp" not in self._models:
                from transformers import pipeline
                self._models["nlp"] = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1
                )
            return self._models["nlp"]

    def get_embedding_model(self):
        with self._lock:
            if "embedding" not in self._models:
                from sentence_transformers import SentenceTransformer
                self._models["embedding"] = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            return self._models["embedding"]

model_manager = ModelManager()
