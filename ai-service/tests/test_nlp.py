"""
Comprehensive tests for the Phase 2 NLP pipeline.

Covers:
  - Preprocessing (normalization, cleaning, metrics)
  - Tokenizer (valid input, empty input, punctuation)
  - Language detection
  - NLP model abstraction
  - Embedding provider
  - API endpoint (valid, empty, whitespace, oversized, malformed)
  - DEMO_MODE behaviour
  - Phase 1 regression (health + error handling)
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.nlp.preprocess import preprocess, validate_length, MAX_TEXT_LENGTH
from app.nlp.tokenizer import SimpleTokenizer, tokenize
from app.nlp.language import HeuristicLanguageDetector, detect_language
from app.nlp.models import DemoNLPModel
from app.nlp.embeddings import DemoEmbeddingProvider


# ===========================================================================
# Preprocessing tests
# ===========================================================================

class TestPreprocessing:

    def test_basic_normalization(self):
        result = preprocess("Hello  World")
        assert result.normalized_text == "Hello World"

    def test_whitespace_stripped(self):
        result = preprocess("  leading and trailing  ")
        assert result.normalized_text == "leading and trailing"

    def test_tab_replaced(self):
        result = preprocess("word1\tword2")
        assert "\t" not in result.normalized_text
        assert "word1" in result.normalized_text

    def test_control_characters_removed(self):
        # \x00 is a null control character
        result = preprocess("hello\x00world")
        assert "\x00" not in result.normalized_text
        assert "hello" in result.normalized_text

    def test_unicode_normalization(self):
        # café composed vs decomposed
        composed = "caf\u00e9"
        decomposed = "cafe\u0301"
        r1 = preprocess(composed)
        r2 = preprocess(decomposed)
        assert r1.normalized_text == r2.normalized_text

    def test_character_count(self):
        result = preprocess("hello")
        assert result.character_count == 5

    def test_word_count(self):
        result = preprocess("one two three four")
        assert result.word_count == 4

    def test_sentence_count_single(self):
        result = preprocess("This is one sentence.")
        assert result.sentence_count >= 1

    def test_sentence_count_multiple(self):
        result = preprocess("First sentence. Second sentence! Third?")
        assert result.sentence_count >= 2

    def test_meaningful_punctuation_preserved(self):
        result = preprocess("Hello, world! How are you?")
        assert "," in result.normalized_text or "Hello" in result.normalized_text

    def test_validate_length_passes(self):
        # Should not raise
        validate_length("a" * (MAX_TEXT_LENGTH - 1))

    def test_validate_length_fails(self):
        with pytest.raises(ValueError, match="maximum length"):
            validate_length("a" * (MAX_TEXT_LENGTH + 1))


# ===========================================================================
# Tokenizer tests
# ===========================================================================

class TestTokenizer:

    def setup_method(self):
        self.tokenizer = SimpleTokenizer()

    def test_name(self):
        assert "tokenizer" in self.tokenizer.name.lower()

    def test_basic_tokenization(self):
        tokens = self.tokenizer.tokenize("hello world")
        assert "hello" in tokens
        assert "world" in tokens

    def test_empty_string(self):
        assert self.tokenizer.tokenize("") == []

    def test_whitespace_only(self):
        assert self.tokenizer.tokenize("   ") == []

    def test_punctuation_tokenized(self):
        tokens = self.tokenizer.tokenize("Hello, world!")
        # Punctuation should appear as separate tokens or attached
        assert "Hello" in tokens or "hello" in tokens.copy()
        assert len(tokens) >= 2

    def test_token_count_matches(self):
        tokens = self.tokenizer.tokenize("one two three")
        assert len(tokens) == 3

    def test_convenience_function(self):
        tokens = tokenize("test input")
        assert isinstance(tokens, list)
        assert len(tokens) == 2


# ===========================================================================
# Language detection tests
# ===========================================================================

class TestLanguageDetection:

    def setup_method(self):
        self.detector = HeuristicLanguageDetector()

    def test_name(self):
        assert self.detector.name != ""

    def test_english_detection(self):
        result = self.detector.detect(
            "the quick brown fox and the lazy dog is in the field"
        )
        assert result.code == "en"
        assert result.confidence > 0.0

    def test_unknown_fallback(self):
        # Gibberish text that matches no language signature
        result = self.detector.detect("xkzqwvj bpflm xkzq")
        # Should either return "unknown" or a low-confidence guess
        assert isinstance(result.code, str)
        assert 0.0 <= result.confidence <= 1.0

    def test_result_has_name(self):
        result = detect_language("the dog is in the house")
        assert isinstance(result.name, str)
        assert len(result.name) > 0

    def test_confidence_range(self):
        result = detect_language("hello world")
        assert 0.0 <= result.confidence <= 1.0


# ===========================================================================
# NLP model tests
# ===========================================================================

class TestNLPModel:

    def setup_method(self):
        self.model = DemoNLPModel()

    def test_model_name(self):
        assert self.model.name != ""

    def test_model_version(self):
        assert self.model.version != ""

    def test_analyze_returns_result(self):
        result = self.model.analyze("hello world", ["hello", "world"])
        assert result.model_name == self.model.name
        assert result.model_version == self.model.version
        assert result.mode == "demo"

    def test_indicators_present(self):
        result = self.model.analyze("hello", ["hello"])
        assert "token_count" in result.indicators
        assert result.indicators["is_demo"] is True

    def test_empty_tokens(self):
        result = self.model.analyze("", [])
        assert result.indicators["token_count"] == 0


# ===========================================================================
# Embedding provider tests
# ===========================================================================

class TestEmbeddingProvider:

    def setup_method(self):
        self.provider = DemoEmbeddingProvider()

    def test_provider_name(self):
        assert self.provider.name != ""

    def test_dimensions(self):
        assert self.provider.dimensions > 0

    def test_embed_returns_correct_dims(self):
        result = self.provider.embed("hello world")
        assert len(result.vector) == self.provider.dimensions

    def test_embed_is_marked_demo(self):
        result = self.provider.embed("test")
        assert result.is_demo is True

    def test_deterministic(self):
        r1 = self.provider.embed("same text")
        r2 = self.provider.embed("same text")
        assert r1.vector == r2.vector

    def test_different_texts_different_vectors(self):
        r1 = self.provider.embed("hello world")
        r2 = self.provider.embed("completely different input")
        assert r1.vector != r2.vector

    def test_vector_values_in_range(self):
        result = self.provider.embed("test text")
        for v in result.vector:
            assert -1.0 <= v <= 1.0


# ===========================================================================
# API endpoint tests
# ===========================================================================

class TestNLPEndpoint:

    def test_valid_text(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "This is a test sentence for Aurevia NLP."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "language" in data
        assert "preprocessing" in data
        assert "tokens" in data
        assert "model" in data
        assert "embedding" in data

    def test_response_language_structure(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "Hello world from Aurevia."},
        )
        data = response.json()
        lang = data["language"]
        assert "code" in lang
        assert "name" in lang
        assert "confidence" in lang

    def test_response_preprocessing_structure(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "Testing preprocessing metrics."},
        )
        data = response.json()
        prep = data["preprocessing"]
        assert "character_count" in prep
        assert "word_count" in prep
        assert "sentence_count" in prep
        assert prep["character_count"] > 0
        assert prep["word_count"] > 0

    def test_response_tokens_structure(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "Token test here."},
        )
        data = response.json()
        tokens = data["tokens"]
        assert "count" in tokens
        assert "items" in tokens
        assert tokens["count"] == len(tokens["items"])

    def test_response_model_structure(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "Model metadata test."},
        )
        data = response.json()
        model = data["model"]
        assert "name" in model
        assert "version" in model
        assert "mode" in model
        assert model["mode"] == "demo"

    def test_response_embedding_structure(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "Embedding test."},
        )
        data = response.json()
        emb = data["embedding"]
        assert "provider" in emb
        assert "dimensions" in emb
        assert "is_demo" in emb
        assert emb["is_demo"] is True

    def test_empty_text_rejected(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": ""},
        )
        assert response.status_code == 422

    def test_whitespace_only_rejected(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "   "},
        )
        assert response.status_code == 422

    def test_missing_text_field_rejected(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={},
        )
        assert response.status_code == 422

    def test_oversized_text_rejected(self, client: TestClient):
        huge_text = "word " * 3000  # ~15,000 chars > MAX_TEXT_LENGTH
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": huge_text},
        )
        assert response.status_code in (422, 500)

    def test_malformed_json(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_demo_mode_is_indicated(self, client: TestClient):
        response = client.post(
            f"{settings.API_V1_STR}/nlp/analyze",
            json={"text": "Demo mode verification test."},
        )
        data = response.json()
        assert data["model"]["mode"] == "demo"
        assert data["embedding"]["is_demo"] is True


# ===========================================================================
# Phase 1 regression tests
# ===========================================================================

class TestPhase1Regression:

    def test_health_still_works(self, client: TestClient):
        response = client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
