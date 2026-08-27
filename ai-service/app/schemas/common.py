from pydantic import BaseModel
from typing import Optional

class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    timestamp: str

class ErrorResponseSchema(BaseModel):
    error: ErrorDetail
