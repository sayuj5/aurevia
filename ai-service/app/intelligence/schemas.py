from pydantic import BaseModel
from typing import List, Optional

class RiskPayloadRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

class SentimentDetail(BaseModel):
    label: str
    confidence: float

class RiskAnalysisDetail(BaseModel):
    score: float
    level: str
    reasoning: List[str]

class IntelligenceResponse(BaseModel):
    mode: str
    sentiment: SentimentDetail
    risk_analysis: RiskAnalysisDetail
