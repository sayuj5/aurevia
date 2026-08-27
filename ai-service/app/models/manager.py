"""
Centralised Model Manager.

Handles lazy-loading, caching, and unloading of real AI models.
This ensures models are only loaded into memory when required by an endpoint
and are reused across requests.
"""

from typing import Any, Callable, Dict
import threading

from app.core.logging import logger

# Types for lazy loaders
ModelLoader = Callable[[], Any]

class ModelManager:
    """
    Manages the lifecycle of AI models in memory.
    Thread-safe lazy initialization.
    """
    
    def __init__(self) -> None:
        self._models: Dict[str, Any] = {}
        self._loaders: Dict[str, ModelLoader] = {}
        self._lock = threading.Lock()

    def register_loader(self, key: str, loader: ModelLoader) -> None:
        """Register a function that loads the model when called."""
        with self._lock:
            self._loaders[key] = loader
            logger.debug("ModelManager: Registered loader for '%s'", key)

    def get_model(self, key: str) -> Any:
        """
        Get a loaded model by key.
        If it is not loaded, it will be initialized using its registered loader.
        Raises ValueError if the loader is missing.
        Raises Exception if loading fails.
        """
        # Fast path
        if key in self._models:
            return self._models[key]

        # Slow path with lock
        with self._lock:
            # Double-check
            if key in self._models:
                return self._models[key]
            
            if key not in self._loaders:
                raise ValueError(f"No loader registered for model key: '{key}'")
            
            logger.info("ModelManager: Lazy-loading model '%s'...", key)
            try:
                model_instance = self._loaders[key]()
                self._models[key] = model_instance
                logger.info("ModelManager: Successfully loaded model '%s'", key)
                return model_instance
            except Exception as exc:
                logger.error("ModelManager: Failed to load model '%s': %s", key, exc)
                raise RuntimeError(f"Failed to load model '{key}': {exc}") from exc

    def unload_model(self, key: str) -> None:
        """Remove a model from memory."""
        with self._lock:
            if key in self._models:
                del self._models[key]
                logger.info("ModelManager: Unloaded model '%s'", key)

    def unload_all(self) -> None:
        """Remove all models from memory."""
        with self._lock:
            keys = list(self._models.keys())
            self._models.clear()
            logger.info("ModelManager: Unloaded all models (%s)", keys)

    def is_loaded(self, key: str) -> bool:
        """Check if a model is currently in memory."""
        return key in self._models


# Global singleton instance
model_manager = ModelManager()
