from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    timestamp: str

class AIException(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.code = code
        self.message = message
        self.status_code = status_code

async def ai_exception_handler(request: Request, exc: AIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    )
