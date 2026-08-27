from fastapi import APIRouter
from datetime import datetime, timezone
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for the AI service.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
