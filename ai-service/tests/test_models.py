"""
Tests for Phase 4 Real AI Models.

Uses `unittest.mock` to simulate huggingface/sentence-transformers 
behavior so tests run fast without downloading large models.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock

# Global mock for torch and transformers so we don't need them installed for unit tests
mock_torch = MagicMock()
mock_torch.cuda.is_available.return_value = False
sys.modules['torch'] = mock_torch

mock_st = MagicMock()
sys.modules['sentence_transformers'] = mock_st

mock_transformers = MagicMock()
sys.modules['transformers'] = mock_transformers

mock_sf = MagicMock()
sys.modules['soundfile'] = mock_sf

from app.nlp.models import RealNLPModel
from app.nlp.embeddings import SentenceTransformerEmbeddingProvider
from app.audio.transcription import WhisperTranscriptionProvider
from app.models.manager import model_manager

# Ensure manager is clear before each test
@pytest.fixture(autouse=True)
def clear_model_manager():
    model_manager.unload_all()
    model_manager._loaders.clear()
    yield
    model_manager.unload_all()
    model_manager._loaders.clear()

def test_real_nlp_model_lazy_load_and_inference():
    model = RealNLPModel(model_name="mock-nlp", device="cpu")
    assert model.name == "mock-nlp"
    
    mock_pipeline_instance = MagicMock()
    mock_pipeline_instance.return_value = [{'label': 'POSITIVE', 'score': 0.99}]
    mock_transformers.pipeline.return_value = mock_pipeline_instance

    result = model.analyze("I love this!", ["I", "love", "this", "!"])
    
    mock_transformers.pipeline.assert_called_once_with("text-classification", model="mock-nlp", device=-1)
    mock_pipeline_instance.assert_called_once()
    
    assert result.indicators["POSITIVE"] == 0.99
    assert result.mode == "production"

def test_sentence_transformer_lazy_load_and_inference():
    provider = SentenceTransformerEmbeddingProvider(model_name="mock-st", device="cpu")
    assert provider.name == "sentence-transformers/mock-st"
    
    mock_st_instance = MagicMock()
    mock_st_instance.encode.return_value = [0.1, 0.2, 0.3]
    mock_st.SentenceTransformer.return_value = mock_st_instance

    result = provider.embed("test text")
    
    mock_st.SentenceTransformer.assert_called_once_with("mock-st", device="cpu")
    mock_st_instance.encode.assert_called_once()
    
    assert result.dimensions == 3
    assert result.vector == [0.1, 0.2, 0.3]
    assert result.is_demo is False

def test_whisper_lazy_load_and_inference():
    provider = WhisperTranscriptionProvider(model_name="mock-whisper", device="cpu")
    assert provider.name == "whisper/mock-whisper"
    
    mock_pipeline_instance = MagicMock()
    mock_pipeline_instance.return_value = {"text": " hello world "}
    mock_transformers.pipeline.return_value = mock_pipeline_instance
    
    mock_sf.read.return_value = ([0.0, 0.0], 16000)

    result = provider.transcribe(b"fake_audio", "wav", 16000)
    
    mock_transformers.pipeline.assert_called_with("automatic-speech-recognition", model="mock-whisper", device=-1)
    
    assert result.available is True
    assert result.text == "hello world"
    assert result.provider == "whisper/mock-whisper"

def test_model_manager_caching():
    loader_calls = 0
    def mock_loader():
        nonlocal loader_calls
        loader_calls += 1
        return "mock_instance"
    
    model_manager.register_loader("test_key", mock_loader)
    
    # First get should call loader
    inst1 = model_manager.get_model("test_key")
    assert loader_calls == 1
    
    # Second get should used cached instance
    inst2 = model_manager.get_model("test_key")
    assert loader_calls == 1
    
    assert inst1 is inst2
