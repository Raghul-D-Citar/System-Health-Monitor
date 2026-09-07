"""Tests for the servers metrics endpoint (Phase 3)."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

client = TestClient(app)


class TestServersMetricsEndpoint:
    """Tests for GET /api/servers/{server_id}/metrics endpoint."""

    def test_get_server_metrics_success(self):
        """Test successful metrics retrieval from Metrics Agent."""
        # Mock response from Metrics Agent
        mock_agent_response = {
            "cpu": {
                "usage_percent": 25.5,
                "core_count": 4,
                "core_count_logical": 8,
                "frequency_current": 2400.0,
                "frequency_max": 3600.0,
            },
            "memory": {
                "total": 16000000000,
                "used": 8000000000,
                "available": 8000000000,
                "percent": 50.0,
            },
            "disk": {
                "total": 1000000000000,
                "used": 500000000000,
                "free": 500000000000,
                "percent": 50.0,
            },
            "network": {
                "bytes_sent": 1000000,
                "bytes_received": 2000000,
                "packets_sent": 10000,
                "packets_received": 15000,
            },
            "system": {
                "hostname": "ubuntu-server",
                "os_info": "Linux",
                "kernel_version": "5.15.0-56-generic",
                "uptime_seconds": 864000,
            },
        }

        # Mock httpx.AsyncClient to return the mocked response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_agent_response

        with patch("app.api.routes.servers.httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            assert response.status_code == 200
            data = response.json()
            assert "cpu" in data
            assert "memory" in data
            assert "disk" in data
            assert "network" in data
            assert "system" in data
            assert data["cpu"]["usage_percent"] == 25.5
            assert data["memory"]["percent"] == 50.0

    def test_get_server_metrics_agent_unreachable(self):
        """Test error handling when Metrics Agent is unreachable."""
        # Mock httpx to raise ConnectError
        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            assert response.status_code == 503
            data = response.json()
            assert data["detail"] is not None
            assert "Cannot reach" in data["detail"]

    def test_get_server_metrics_timeout(self):
        """Test error handling when Metrics Agent request times out."""
        # Mock httpx to raise TimeoutException
        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(
                side_effect=httpx.TimeoutException("Request timed out")
            )
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            assert response.status_code == 504
            data = response.json()
            assert data["detail"] is not None
            assert "timed out" in data["detail"].lower()

    def test_get_server_metrics_agent_error(self):
        """Test error handling when Metrics Agent returns an error."""
        # Mock response from Metrics Agent with error status
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}

        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            assert response.status_code == 502
            data = response.json()
            assert data["detail"] is not None
            assert "returned status 500" in data["detail"]

    def test_get_server_metrics_invalid_json(self):
        """Test error handling when Metrics Agent returns invalid JSON."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            assert response.status_code == 502
            data = response.json()
            assert data["detail"] is not None
            assert "invalid json" in data["detail"].lower()

    def test_get_server_metrics_uses_configured_url(self):
        """Test that the endpoint uses the configured agent URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cpu": {"usage_percent": 25.5}}

        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            # Verify the agent URL was used
            assert response.status_code == 200
            mock_client_instance.get.assert_called_once()
            call_args = mock_client_instance.get.call_args

            # The URL should be the configured agent URL + /api/metrics
            expected_url = f"{settings.agent_url}/api/metrics"
            assert call_args[0][0] == expected_url

    def test_get_server_metrics_uses_configured_timeout(self):
        """Test that the endpoint uses the configured timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cpu": {"usage_percent": 25.5}}

        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            # Verify the timeout was used
            assert response.status_code == 200
            call_kwargs = mock_client_instance.get.call_args[1]
            assert call_kwargs["timeout"] == settings.agent_timeout

    def test_server_id_parameter_accepted(self):
        """Test that server_id parameter is accepted and passed correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cpu": {"usage_percent": 25.5}}

        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            # Test with different server_id values
            response1 = client.get("/api/servers/server-1/metrics")
            response2 = client.get("/api/servers/ubuntu-prod/metrics")
            response3 = client.get("/api/servers/my-server-123/metrics")

            # All should work (server_id currently ignored but path must match)
            assert response1.status_code == 200
            assert response2.status_code == 200
            assert response3.status_code == 200

    def test_response_structure_includes_all_metrics(self):
        """Test that the response includes all expected metric categories."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cpu": {
                "usage_percent": 25.5,
                "core_count": 4,
                "core_count_logical": 8,
                "frequency_current": 2400.0,
                "frequency_max": 3600.0,
            },
            "memory": {
                "total": 16000000000,
                "used": 8000000000,
                "available": 8000000000,
                "percent": 50.0,
            },
            "disk": {
                "total": 1000000000000,
                "used": 500000000000,
                "free": 500000000000,
                "percent": 50.0,
            },
            "network": {
                "bytes_sent": 1000000,
                "bytes_received": 2000000,
                "packets_sent": 10000,
                "packets_received": 15000,
            },
            "system": {
                "hostname": "ubuntu-server",
                "os_info": "Linux",
                "kernel_version": "5.15.0-56-generic",
                "uptime_seconds": 864000,
            },
        }

        with patch(
            "app.api.routes.servers.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            response = client.get("/api/servers/ubuntu-1/metrics")

            assert response.status_code == 200
            data = response.json()

            # Verify all metric categories are present
            assert "cpu" in data
            assert "memory" in data
            assert "disk" in data
            assert "network" in data
            assert "system" in data

            # Verify nested structure
            assert "usage_percent" in data["cpu"]
            assert "total" in data["memory"]
            assert "total" in data["disk"]
            assert "bytes_sent" in data["network"]
            assert "hostname" in data["system"]

    def test_endpoint_is_documented(self):
        """Test that the endpoint appears in OpenAPI docs."""
        response = client.get("/docs")
        assert response.status_code == 200

        # Check for the servers endpoint in the HTML (basic check)
        # FastAPI includes endpoint paths in OpenAPI JSON, so let's also check that
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi = response.json()

        # Check that the servers endpoint is in the paths
        assert "/api/servers/{server_id}/metrics" in openapi["paths"]
