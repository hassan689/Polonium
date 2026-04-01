from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "running"


def test_health_basic():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

