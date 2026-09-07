"""Tests for the metrics endpoints and collectors."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from agent.main import app
from agent.api.collectors.system import MetricsCollector
from agent.models import (
    CPUMetrics,
    MemoryMetrics,
    DiskMetrics,
    NetworkMetrics,
    SystemMetrics,
    AllMetrics,
)

client = TestClient(app)


# --- CPU Metrics Tests ---


def test_get_cpu_metrics_endpoint(mock_all_metrics):
    """Test that the CPU metrics endpoint returns a 200 status code."""
    response = client.get("/api/metrics/cpu")
    assert response.status_code == 200


def test_get_cpu_metrics_response_structure(mock_all_metrics):
    """Test that the CPU metrics endpoint returns the expected response structure."""
    response = client.get("/api/metrics/cpu")
    data = response.json()

    assert "usage_percent" in data
    assert "core_count" in data
    assert "core_count_logical" in data
    assert "frequency_current" in data
    assert "frequency_max" in data


def test_get_cpu_metrics_values(mock_all_metrics):
    """Test that the CPU metrics endpoint returns correct values."""
    response = client.get("/api/metrics/cpu")
    data = response.json()

    assert data["usage_percent"] == 25.5
    assert data["core_count"] == 4
    assert data["core_count_logical"] == 8
    assert data["frequency_current"] == 2400.0
    assert data["frequency_max"] == 3600.0


def test_collector_cpu_metrics_no_frequency(mocker):
    """Test CPU metrics collection when frequency info is unavailable."""
    mocker.patch("psutil.cpu_percent", return_value=30.0)
    mocker.patch("psutil.cpu_count", side_effect=lambda logical=True: 8 if logical else 4)
    mocker.patch("psutil.cpu_freq", return_value=None)

    metrics = MetricsCollector.get_cpu_metrics()

    assert metrics.usage_percent == 30.0
    assert metrics.core_count == 4
    assert metrics.core_count_logical == 8
    assert metrics.frequency_current is None
    assert metrics.frequency_max is None


# --- Memory Metrics Tests ---


def test_get_memory_metrics_endpoint(mock_all_metrics):
    """Test that the memory metrics endpoint returns a 200 status code."""
    response = client.get("/api/metrics/memory")
    assert response.status_code == 200


def test_get_memory_metrics_response_structure(mock_all_metrics):
    """Test that the memory metrics endpoint returns the expected response structure."""
    response = client.get("/api/metrics/memory")
    data = response.json()

    assert "total" in data
    assert "used" in data
    assert "available" in data
    assert "percent" in data


def test_get_memory_metrics_values(mock_all_metrics):
    """Test that the memory metrics endpoint returns correct values."""
    response = client.get("/api/metrics/memory")
    data = response.json()

    assert data["total"] == 16000000000
    assert data["used"] == 8000000000
    assert data["available"] == 8000000000
    assert data["percent"] == 50.0


# --- Disk Metrics Tests ---


def test_get_disk_metrics_endpoint(mock_all_metrics):
    """Test that the disk metrics endpoint returns a 200 status code."""
    response = client.get("/api/metrics/disk")
    assert response.status_code == 200


def test_get_disk_metrics_response_structure(mock_all_metrics):
    """Test that the disk metrics endpoint returns the expected response structure."""
    response = client.get("/api/metrics/disk")
    data = response.json()

    assert "total" in data
    assert "used" in data
    assert "free" in data
    assert "percent" in data


def test_get_disk_metrics_values(mock_all_metrics):
    """Test that the disk metrics endpoint returns correct values."""
    response = client.get("/api/metrics/disk")
    data = response.json()

    assert data["total"] == 1000000000000
    assert data["used"] == 500000000000
    assert data["free"] == 500000000000
    assert data["percent"] == 50.0


# --- Network Metrics Tests ---


def test_get_network_metrics_endpoint(mock_all_metrics):
    """Test that the network metrics endpoint returns a 200 status code."""
    response = client.get("/api/metrics/network")
    assert response.status_code == 200


def test_get_network_metrics_response_structure(mock_all_metrics):
    """Test that the network metrics endpoint returns the expected response structure."""
    response = client.get("/api/metrics/network")
    data = response.json()

    assert "bytes_sent" in data
    assert "bytes_received" in data
    assert "packets_sent" in data
    assert "packets_received" in data


def test_get_network_metrics_values(mock_all_metrics):
    """Test that the network metrics endpoint returns correct values."""
    response = client.get("/api/metrics/network")
    data = response.json()

    assert data["bytes_sent"] == 1000000
    assert data["bytes_received"] == 2000000
    assert data["packets_sent"] == 10000
    assert data["packets_received"] == 15000


# --- System Metrics Tests ---


def test_get_system_metrics_endpoint(mock_all_metrics):
    """Test that the system metrics endpoint returns a 200 status code."""
    response = client.get("/api/metrics/system")
    assert response.status_code == 200


def test_get_system_metrics_response_structure(mock_all_metrics):
    """Test that the system metrics endpoint returns the expected response structure."""
    response = client.get("/api/metrics/system")
    data = response.json()

    assert "hostname" in data
    assert "os_info" in data
    assert "kernel_version" in data
    assert "uptime_seconds" in data


def test_collector_system_metrics(mocker):
    """Test system metrics collection."""
    mocker.patch("platform.node", return_value="test-host")
    mocker.patch("platform.system", return_value="Linux")
    mocker.patch("platform.release", return_value="5.15.0-56-generic")
    mocker.patch("os.times", return_value=(0, 0, 0, 0, 864000))

    metrics = MetricsCollector.get_system_metrics()

    assert metrics.hostname == "test-host"
    assert metrics.os_info == "Linux"
    assert metrics.kernel_version == "5.15.0-56-generic"
    assert metrics.uptime_seconds == 864000


# --- All Metrics Combined Tests ---


def test_get_all_metrics_endpoint(mock_all_metrics):
    """Test that the all metrics endpoint returns a 200 status code."""
    response = client.get("/api/metrics")
    assert response.status_code == 200


def test_get_all_metrics_response_structure(mock_all_metrics):
    """Test that the all metrics endpoint returns all metric categories."""
    response = client.get("/api/metrics")
    data = response.json()

    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "network" in data
    assert "system" in data


def test_get_all_metrics_cpu_structure(mock_all_metrics):
    """Test that CPU metrics have correct structure in combined response."""
    response = client.get("/api/metrics")
    data = response.json()
    cpu = data["cpu"]

    assert "usage_percent" in cpu
    assert "core_count" in cpu
    assert "core_count_logical" in cpu


def test_get_all_metrics_memory_structure(mock_all_metrics):
    """Test that memory metrics have correct structure in combined response."""
    response = client.get("/api/metrics")
    data = response.json()
    memory = data["memory"]

    assert "total" in memory
    assert "used" in memory
    assert "available" in memory
    assert "percent" in memory


def test_get_all_metrics_disk_structure(mock_all_metrics):
    """Test that disk metrics have correct structure in combined response."""
    response = client.get("/api/metrics")
    data = response.json()
    disk = data["disk"]

    assert "total" in disk
    assert "used" in disk
    assert "free" in disk
    assert "percent" in disk


def test_get_all_metrics_network_structure(mock_all_metrics):
    """Test that network metrics have correct structure in combined response."""
    response = client.get("/api/metrics")
    data = response.json()
    network = data["network"]

    assert "bytes_sent" in network
    assert "bytes_received" in network
    assert "packets_sent" in network
    assert "packets_received" in network


def test_get_all_metrics_system_structure(mock_all_metrics):
    """Test that system metrics have correct structure in combined response."""
    response = client.get("/api/metrics")
    data = response.json()
    system = data["system"]

    assert "hostname" in system
    assert "os_info" in system
    assert "kernel_version" in system
    assert "uptime_seconds" in system


# --- Error Handling Tests ---


def test_cpu_metrics_collection_error(mocker):
    """Test error handling when CPU metrics collection fails."""
    mocker.patch("psutil.cpu_percent", side_effect=Exception("CPU metrics error"))

    response = client.get("/api/metrics/cpu")
    assert response.status_code == 500

    data = response.json()
    assert "status" in data
    assert data["status"] == "error"


def test_memory_metrics_collection_error(mocker):
    """Test error handling when memory metrics collection fails."""
    mocker.patch("psutil.virtual_memory", side_effect=Exception("Memory error"))

    response = client.get("/api/metrics/memory")
    assert response.status_code == 500


def test_disk_metrics_collection_error(mocker):
    """Test error handling when disk metrics collection fails."""
    mocker.patch("psutil.disk_usage", side_effect=Exception("Disk error"))

    response = client.get("/api/metrics/disk")
    assert response.status_code == 500


def test_network_metrics_collection_error(mocker):
    """Test error handling when network metrics collection fails."""
    mocker.patch("psutil.net_io_counters", side_effect=Exception("Network error"))

    response = client.get("/api/metrics/network")
    assert response.status_code == 500


# --- Collector Tests ---


def test_collector_cpu_metrics(mock_all_metrics):
    """Test that CPU metrics collector returns CPUMetrics instance."""
    metrics = MetricsCollector.get_cpu_metrics()
    assert isinstance(metrics, CPUMetrics)
    assert metrics.usage_percent == 25.5


def test_collector_memory_metrics(mock_all_metrics):
    """Test that memory metrics collector returns MemoryMetrics instance."""
    metrics = MetricsCollector.get_memory_metrics()
    assert isinstance(metrics, MemoryMetrics)
    assert metrics.total == 16000000000


def test_collector_disk_metrics(mock_all_metrics):
    """Test that disk metrics collector returns DiskMetrics instance."""
    metrics = MetricsCollector.get_disk_metrics()
    assert isinstance(metrics, DiskMetrics)
    assert metrics.total == 1000000000000


def test_collector_network_metrics(mock_all_metrics):
    """Test that network metrics collector returns NetworkMetrics instance."""
    metrics = MetricsCollector.get_network_metrics()
    assert isinstance(metrics, NetworkMetrics)
    assert metrics.bytes_sent == 1000000


def test_collector_all_metrics(mock_all_metrics):
    """Test that all metrics collector returns AllMetrics instance."""
    metrics = MetricsCollector.get_all_metrics()
    assert isinstance(metrics, AllMetrics)
    assert isinstance(metrics.cpu, CPUMetrics)
    assert isinstance(metrics.memory, MemoryMetrics)
    assert isinstance(metrics.disk, DiskMetrics)
    assert isinstance(metrics.network, NetworkMetrics)
    assert isinstance(metrics.system, SystemMetrics)
