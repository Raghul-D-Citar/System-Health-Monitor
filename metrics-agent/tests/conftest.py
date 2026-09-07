"""Pytest configuration and fixtures for Metrics Agent tests."""

import pytest
from unittest.mock import MagicMock

import psutil


@pytest.fixture
def mock_cpu_percent(mocker):
    """Mock psutil.cpu_percent to return a fixed value."""
    return mocker.patch("psutil.cpu_percent", return_value=25.5)


@pytest.fixture
def mock_cpu_count(mocker):
    """Mock psutil.cpu_count to return fixed core counts."""

    def side_effect(logical=True):
        return 8 if logical else 4

    return mocker.patch("psutil.cpu_count", side_effect=side_effect)


@pytest.fixture
def mock_cpu_freq(mocker):
    """Mock psutil.cpu_freq to return CPU frequency."""
    freq = MagicMock()
    freq.current = 2400.0
    freq.max = 3600.0
    return mocker.patch("psutil.cpu_freq", return_value=freq)


@pytest.fixture
def mock_virtual_memory(mocker):
    """Mock psutil.virtual_memory to return memory stats."""
    mem = MagicMock()
    mem.total = 16000000000
    mem.used = 8000000000
    mem.available = 8000000000
    mem.percent = 50.0
    return mocker.patch("psutil.virtual_memory", return_value=mem)


@pytest.fixture
def mock_disk_usage(mocker):
    """Mock psutil.disk_usage to return disk stats."""
    disk = MagicMock()
    disk.total = 1000000000000
    disk.used = 500000000000
    disk.free = 500000000000
    disk.percent = 50.0
    return mocker.patch("psutil.disk_usage", return_value=disk)


@pytest.fixture
def mock_net_io_counters(mocker):
    """Mock psutil.net_io_counters to return network stats."""
    net_io = MagicMock()
    net_io.bytes_sent = 1000000
    net_io.bytes_recv = 2000000
    net_io.packets_sent = 10000
    net_io.packets_recv = 15000
    return mocker.patch("psutil.net_io_counters", return_value=net_io)


@pytest.fixture
def mock_all_metrics(
    mock_cpu_percent,
    mock_cpu_count,
    mock_cpu_freq,
    mock_virtual_memory,
    mock_disk_usage,
    mock_net_io_counters,
):
    """Mock all psutil functions needed for metrics collection."""
    return {
        "cpu_percent": mock_cpu_percent,
        "cpu_count": mock_cpu_count,
        "cpu_freq": mock_cpu_freq,
        "virtual_memory": mock_virtual_memory,
        "disk_usage": mock_disk_usage,
        "net_io_counters": mock_net_io_counters,
    }
