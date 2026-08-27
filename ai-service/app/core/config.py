from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "Aurevia AI Service"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Behavior
    DEMO_MODE: bool = True
    
    # ------------------------------------------------------------------
    # AI Models (Phase 4)
    # ------------------------------------------------------------------
    AI_MODE: str = "demo" # "demo" or "real"
    AI_DEVICE: str = "cpu" # "cpu", "cuda", "mps"

    NLP_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    STT_MODEL_NAME: str = "openai/whisper-tiny"

    AI_MAX_INPUT_LENGTH: int = 10000

    # ------------------------------------------------------------------
    # Audio upload settings
    # ------------------------------------------------------------------
    AUDIO_MAX_SIZE_MB: int = 50
    AUDIO_ALLOWED_EXTENSIONS: List[str] = ["wav", "mp3", "ogg", "m4a", "flac"]
    AUDIO_ALLOWED_MIME_TYPES: List[str] = [
        "audio/wav", "audio/x-wav", "audio/wave",
        "audio/mpeg", "audio/mp3",
        "audio/ogg", "application/ogg",
        "audio/mp4", "audio/x-m4a",
        "audio/flac", "audio/x-flac",
    ]

    # ------------------------------------------------------------------
    # Object storage settings
    # ------------------------------------------------------------------
    STORAGE_PROVIDER: str = "local"          # "local" | "minio"
    LOCAL_STORAGE_PATH: str = "./data/audio"

    # MinIO (only used when STORAGE_PROVIDER="minio")
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET_NAME: str = "aurevia-audio"
    MINIO_SECURE: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
