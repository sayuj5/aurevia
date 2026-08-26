from fastapi import APIRouter, HTTPException
from app.intelligence.schemas import RiskPayloadRequest, IntelligenceResponse
from app.intelligence.service import risk_service

router = APIRouter()

@router.post("/analyze", response_model=IntelligenceResponse)
async def analyze_text_risk(payload: RiskPayloadRequest):
    """
    Ingests text payload, runs NLP sentiment analysis, and calculates forensic risk score.
    """
    try:
        # Feed the text directly into the engine we just built
        result = risk_service.analyze_payload(payload.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence processing failed: {str(e)}")