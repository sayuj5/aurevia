from app.core.config import settings

def test_health_check(client):
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == settings.APP_NAME
    assert "version" in data
    assert "timestamp" in data
