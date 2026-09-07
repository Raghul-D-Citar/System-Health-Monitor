"""System metrics collector using psutil.

This module collects various system metrics from the host machine using psutil.
It is designed to be testable with mocked psutil dependencies.
"""

import os
import platform
from typing import Optional

import psutil

from agent.models import (
    AllMetrics,
    CPUMetrics,
    DiskMetrics,
    MemoryMetrics,
    NetworkMetrics,
    SystemMetrics,
)


class MetricsCollector:
    """Collects system metrics from the host machine."""

    @staticmethod
    def get_cpu_metrics() -> CPUMetrics:
        """Collect CPU metrics.

        Returns:
            CPUMetrics: CPU usage percentage, core count, and frequency.

        Raises:
            Exception: If metrics cannot be collected.
        """
        try:
            usage_percent = psutil.cpu_percent(interval=0.1)
            core_count = psutil.cpu_count(logical=False) or 1
            core_count_logical = psutil.cpu_count(logical=True) or 1

            # Frequency information might not be available on all systems
            frequency_current: Optional[float] = None
            frequency_max: Optional[float] = None
            try:
                freq = psutil.cpu_freq()
                if freq:
                    frequency_current = freq.current
                    frequency_max = freq.max
            except (AttributeError, OSError, RuntimeError):
                # Frequency info not available on this system
                pass

            return CPUMetrics(
                usage_percent=usage_percent,
                core_count=core_count,
                core_count_logical=core_count_logical,
                frequency_current=frequency_current,
                frequency_max=frequency_max,
            )
        except Exception as e:
            raise Exception(f"Failed to collect CPU metrics: {str(e)}")

    @staticmethod
    def get_memory_metrics() -> MemoryMetrics:
        """Collect memory metrics.

        Returns:
            MemoryMetrics: Memory usage information.

        Raises:
            Exception: If metrics cannot be collected.
        """
        try:
            mem = psutil.virtual_memory()
            return MemoryMetrics(
                total=mem.total,
                used=mem.used,
                available=mem.available,
                percent=mem.percent,
            )
        except Exception as e:
            raise Exception(f"Failed to collect memory metrics: {str(e)}")

    @staticmethod
    def get_disk_metrics() -> DiskMetrics:
        """Collect disk metrics for the root partition.

        Returns:
            DiskMetrics: Disk usage information.

        Raises:
            Exception: If metrics cannot be collected.
        """
        try:
            disk = psutil.disk_usage("/")
            return DiskMetrics(
                total=disk.total,
                used=disk.used,
                free=disk.free,
                percent=disk.percent,
            )
        except Exception as e:
            raise Exception(f"Failed to collect disk metrics: {str(e)}")

    @staticmethod
    def get_network_metrics() -> NetworkMetrics:
        """Collect network metrics.

        Returns:
            NetworkMetrics: Network I/O statistics.

        Raises:
            Exception: If metrics cannot be collected.
        """
        try:
            net_io = psutil.net_io_counters()
            return NetworkMetrics(
                bytes_sent=net_io.bytes_sent,
                bytes_received=net_io.bytes_recv,
                packets_sent=net_io.packets_sent,
                packets_received=net_io.packets_recv,
            )
        except Exception as e:
            raise Exception(f"Failed to collect network metrics: {str(e)}")

    @staticmethod
    def get_system_metrics() -> SystemMetrics:
        """Collect system information metrics.

        Returns:
            SystemMetrics: System information and uptime.

        Raises:
            Exception: If metrics cannot be collected.
        """
        try:
            hostname = platform.node()
            os_info = platform.system()
            kernel_version = platform.release()
            uptime_seconds = int(os.times()[4])  # System uptime in seconds

            return SystemMetrics(
                hostname=hostname,
                os_info=os_info,
                kernel_version=kernel_version,
                uptime_seconds=uptime_seconds,
            )
        except Exception as e:
            raise Exception(f"Failed to collect system metrics: {str(e)}")

    @classmethod
    def get_all_metrics(cls) -> AllMetrics:
        """Collect all metrics at once.

        Returns:
            AllMetrics: All system metrics combined.

        Raises:
            Exception: If any metric collection fails.
        """
        return AllMetrics(
            cpu=cls.get_cpu_metrics(),
            memory=cls.get_memory_metrics(),
            disk=cls.get_disk_metrics(),
            network=cls.get_network_metrics(),
            system=cls.get_system_metrics(),
        )
