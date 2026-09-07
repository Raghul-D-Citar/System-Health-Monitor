"""Tests for the health check endpoint."""

import pytest
from fastapi.testclient import TestClient

from agent.main import app
from agent.config import settings

client = TestClient(app)


def test_health_check_endpoint():
    """Test that the health endpoint returns a 200 status code."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_check_response_structure():
    """Test that the health endpoint returns the expected response structure."""
    response = client.get("/api/health")
    data = response.json()

    assert "status" in data
    assert "service" in data
    assert "version" in data


def test_health_check_response_values():
    """Test that the health endpoint returns correct values."""
    response = client.get("/api/health")
    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == settings.app_name
    assert data["version"] == settings.app_version


def test_root_endpoint():
    """Test that the root endpoint returns service information."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "message" in data
    assert "docs" in data
    assert "health" in data
    assert "metrics" in data
