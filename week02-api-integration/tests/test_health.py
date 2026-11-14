from fastapi.testclient import TestClient

from api_service.main import app


def test_root_message():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Agentic AI API is running"}


def test_health_check():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body and "version" in body


def test_unknown_route_returns_404():
    response = TestClient(app).get("/does-not-exist")
    assert response.status_code == 404
