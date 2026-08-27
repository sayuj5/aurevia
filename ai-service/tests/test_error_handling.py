from fastapi import APIRouter
from app.core.exceptions import AIException
from app.main import app
from app.core.config import settings

router = APIRouter()

@router.get("/test-error")
async def trigger_error():
    raise AIException(code="TEST_ERROR", message="This is a test error", status_code=400)

@router.get("/test-fatal")
async def trigger_fatal():
    raise ValueError("This is a fatal unhandled error")

app.include_router(router, prefix=settings.API_V1_STR)

def test_ai_exception_handler(client):
    response = client.get(f"{settings.API_V1_STR}/test-error")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TEST_ERROR"
    assert data["error"]["message"] == "This is a test error"
    assert "timestamp" in data["error"]

def test_generic_exception_handler(client):
    response = client.get(f"{settings.API_V1_STR}/test-fatal")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
