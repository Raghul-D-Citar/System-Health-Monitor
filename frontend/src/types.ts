export interface CpuMetrics {
  usage_percent: number;
  core_count: number;
  core_count_logical: number;
  frequency_current?: number | null;
  frequency_max?: number | null;
}

export interface MemoryMetrics {
  total: number;
  used: number;
  available: number;
  percent: number;
}

export interface DiskMetrics {
  total: number;
  used: number;
  free: number;
  percent: number;
}

export interface NetworkMetrics {
  bytes_sent: number;
  bytes_received: number;
  packets_sent: number;
  packets_received: number;
}

export interface SystemMetrics {
  hostname: string;
  os_info: string;
  kernel_version: string;
  uptime_seconds: number;
}

export interface ServerMetrics {
  cpu: CpuMetrics;
  memory: MemoryMetrics;
  disk: DiskMetrics;
  network: NetworkMetrics;
  system: SystemMetrics;
}

export type DashboardStatus = 'loading' | 'online' | 'offline' | 'error';

export interface DashboardErrorInfo {
  kind: 'aborted' | 'offline' | 'timeout' | 'invalid-response' | 'server-error' | 'unknown';
  message: string;
  statusCode?: number;
}

export interface MetricSnapshot {
  serverId: string;
  serverName: string;
  metrics: ServerMetrics;
  lastSuccessfulUpdate: Date;
}
