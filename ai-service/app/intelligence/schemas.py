"""
Schemas for the combined AI Intelligence layer.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.schemas.nlp import NLPAnalyzeResponse
from app.schemas.audio import AudioAnalyzeResponse

class CombinedIntelligenceResponse(BaseModel):
    """
    Structured output combining multiple modalities.
    To be expanded in future phases.
    """
    success: bool
    nlp_result: Optional[NLPAnalyzeResponse] = None
    audio_result: Optional[AudioAnalyzeResponse] = None
    mode: str
    device: str
