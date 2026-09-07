"""Pydantic models for metrics responses."""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CPUMetrics(BaseModel):
    """CPU metrics response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "usage_percent": 25.5,
                "core_count": 4,
                "core_count_logical": 8,
                "frequency_current": 2400.0,
                "frequency_max": 3600.0,
            }
        }
    )

    usage_percent: float = Field(..., description="CPU usage percentage (0-100)")
    core_count: int = Field(..., description="Number of CPU cores")
    core_count_logical: int = Field(
        ..., description="Number of logical CPU cores"
    )
    frequency_current: Optional[float] = Field(
        None, description="Current CPU frequency in MHz"
    )
    frequency_max: Optional[float] = Field(
        None, description="Maximum CPU frequency in MHz"
    )


class MemoryMetrics(BaseModel):
    """Memory metrics response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 16000000000,
                "used": 8000000000,
                "available": 8000000000,
                "percent": 50.0,
            }
        }
    )

    total: int = Field(..., description="Total memory in bytes")
    used: int = Field(..., description="Used memory in bytes")
    available: int = Field(..., description="Available memory in bytes")
    percent: float = Field(..., description="Memory usage percentage (0-100)")


class DiskMetrics(BaseModel):
    """Disk metrics response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 1000000000000,
                "used": 500000000000,
                "free": 500000000000,
                "percent": 50.0,
            }
        }
    )

    total: int = Field(..., description="Total disk space in bytes")
    used: int = Field(..., description="Used disk space in bytes")
    free: int = Field(..., description="Free disk space in bytes")
    percent: float = Field(..., description="Disk usage percentage (0-100)")


class NetworkMetrics(BaseModel):
    """Network metrics response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bytes_sent": 1000000,
                "bytes_received": 2000000,
                "packets_sent": 10000,
                "packets_received": 15000,
            }
        }
    )

    bytes_sent: int = Field(..., description="Total bytes sent")
    bytes_received: int = Field(..., description="Total bytes received")
    packets_sent: int = Field(..., description="Total packets sent")
    packets_received: int = Field(..., description="Total packets received")


class SystemMetrics(BaseModel):
    """System information metrics response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hostname": "ubuntu-server",
                "os_info": "Linux",
                "kernel_version": "5.15.0-56-generic",
                "uptime_seconds": 864000,
            }
        }
    )

    hostname: str = Field(..., description="System hostname")
    os_info: str = Field(..., description="Operating system name")
    kernel_version: str = Field(..., description="Kernel version")
    uptime_seconds: int = Field(..., description="System uptime in seconds")


class AllMetrics(BaseModel):
    """All metrics combined response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
        }
    )

    cpu: CPUMetrics = Field(..., description="CPU metrics")
    memory: MemoryMetrics = Field(..., description="Memory metrics")
    disk: DiskMetrics = Field(..., description="Disk metrics")
    network: NetworkMetrics = Field(..., description="Network metrics")
    system: SystemMetrics = Field(..., description="System metrics")


class HealthResponse(BaseModel):
    """Health check response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "service": "Metrics Agent",
                "version": "0.1.0",
            }
        }
    )

    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
