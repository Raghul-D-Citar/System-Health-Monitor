"""Tests for the health endpoint (Phase 1)."""

from fastapi.testclient import TestClient

from app.main import app

# A single test client shared by all tests in this module.
client = TestClient(app)


def test_health_endpoint_returns_ok_status() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "System Health Monitor"
    assert body["version"] == "0.1.0"


def test_health_endpoint_returns_json_content_type() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_root_endpoint_is_reachable() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["health"] == "/api/health"
    assert body["service"] == "System Health Monitor"


def test_unknown_endpoint_returns_json_404() -> None:
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404

    body = response.json()
    assert body["status"] == "error"
    assert body["detail"] == "Not Found"
