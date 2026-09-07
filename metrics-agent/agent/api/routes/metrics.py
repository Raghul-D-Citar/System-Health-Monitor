"""Metrics endpoints.

Exposes system metrics collected from psutil through various API endpoints.
Each endpoint returns specific metrics or all metrics combined.
"""

from fastapi import APIRouter, HTTPException

from agent.api.collectors.system import MetricsCollector
from agent.models import (
    AllMetrics,
    CPUMetrics,
    DiskMetrics,
    MemoryMetrics,
    NetworkMetrics,
    SystemMetrics,
)

router = APIRouter()


@router.get(
    "/metrics",
    tags=["metrics"],
    summary="Get all metrics",
    description="Returns all system metrics (CPU, memory, disk, network, and system info).",
    response_model=AllMetrics,
)
async def get_all_metrics() -> AllMetrics:
    """Return all collected system metrics.

    Returns:
        AllMetrics: Combined metrics from all collectors.

    Raises:
        HTTPException: If metrics collection fails.
    """
    try:
        return MetricsCollector.get_all_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics/cpu",
    tags=["metrics"],
    summary="Get CPU metrics",
    description="Returns CPU usage, core count, and frequency information.",
    response_model=CPUMetrics,
)
async def get_cpu_metrics() -> CPUMetrics:
    """Return CPU metrics.

    Returns:
        CPUMetrics: CPU usage and core information.

    Raises:
        HTTPException: If metrics collection fails.
    """
    try:
        return MetricsCollector.get_cpu_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics/memory",
    tags=["metrics"],
    summary="Get memory metrics",
    description="Returns memory usage information.",
    response_model=MemoryMetrics,
)
async def get_memory_metrics() -> MemoryMetrics:
    """Return memory metrics.

    Returns:
        MemoryMetrics: Memory usage information.

    Raises:
        HTTPException: If metrics collection fails.
    """
    try:
        return MetricsCollector.get_memory_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics/disk",
    tags=["metrics"],
    summary="Get disk metrics",
    description="Returns disk usage information for the root partition.",
    response_model=DiskMetrics,
)
async def get_disk_metrics() -> DiskMetrics:
    """Return disk metrics.

    Returns:
        DiskMetrics: Disk usage information.

    Raises:
        HTTPException: If metrics collection fails.
    """
    try:
        return MetricsCollector.get_disk_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics/network",
    tags=["metrics"],
    summary="Get network metrics",
    description="Returns network I/O statistics.",
    response_model=NetworkMetrics,
)
async def get_network_metrics() -> NetworkMetrics:
    """Return network metrics.

    Returns:
        NetworkMetrics: Network I/O statistics.

    Raises:
        HTTPException: If metrics collection fails.
    """
    try:
        return MetricsCollector.get_network_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics/system",
    tags=["metrics"],
    summary="Get system metrics",
    description="Returns system information and uptime.",
    response_model=SystemMetrics,
)
async def get_system_metrics() -> SystemMetrics:
    """Return system metrics.

    Returns:
        SystemMetrics: System information and uptime.

    Raises:
        HTTPException: If metrics collection fails.
    """
    try:
        return MetricsCollector.get_system_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
