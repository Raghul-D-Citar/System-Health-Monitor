import { useEffect, useRef, useState } from 'react';

import { MetricCard } from './components/MetricCard';
import { StatusPill } from './components/StatusPill';
import {
  DashboardApiError,
  buildMetricsPath,
  fetchServerMetrics,
  getDefaultServerId,
  getRequestTimeoutMs,
} from './lib/api';
import {
  formatBytes,
  formatDateTime,
  formatFrequency,
  formatInteger,
  formatPercent,
  formatUptime,
} from './lib/format';
import type { DashboardErrorInfo, DashboardStatus, ServerMetrics } from './types';

const serverId = getDefaultServerId();
const serverName = import.meta.env.VITE_SHM_SERVER_NAME?.trim() || 'Ubuntu VM';
const refreshIntervalMs = Number(import.meta.env.VITE_SHM_REFRESH_INTERVAL_MS || '5000');
const requestTimeoutMs = getRequestTimeoutMs();

function normalizeError(error: unknown): DashboardErrorInfo {
  if (error instanceof DashboardApiError) {
    return error;
  }

  if (error instanceof Error) {
    return {
      kind: 'unknown',
      message: error.message || 'Unexpected error while loading metrics.',
    };
  }

  return {
    kind: 'unknown',
    message: 'Unexpected error while loading metrics.',
  };
}

function resolveStatus(error: DashboardErrorInfo): DashboardStatus {
  if (error.kind === 'offline' || error.kind === 'timeout' || error.kind === 'aborted') {
    return 'offline';
  }

  if (error.kind === 'invalid-response' || error.kind === 'server-error') {
    return 'error';
  }

  return 'error';
}

function renderSystemValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') {
    return 'Not available';
  }

  if (typeof value === 'number') {
    return formatInteger(value);
  }

  return value;
}

export default function App() {
  const [metrics, setMetrics] = useState<ServerMetrics | null>(null);
  const [status, setStatus] = useState<DashboardStatus>('loading');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastSuccessfulUpdate, setLastSuccessfulUpdate] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const metricsRef = useRef<ServerMetrics | null>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const timerRef = useRef<number | null>(null);
  const disposedRef = useRef(false);

  useEffect(() => {
    metricsRef.current = metrics;
  }, [metrics]);

  useEffect(() => {
    disposedRef.current = false;

    const poll = async (): Promise<void> => {
      const controller = new AbortController();
      controllerRef.current = controller;

      if (metricsRef.current) {
        setIsRefreshing(true);
      } else {
        setStatus('loading');
      }

      try {
        const response = await fetchServerMetrics({
          serverId,
          timeoutMs: requestTimeoutMs,
          signal: controller.signal,
        });

        if (disposedRef.current) {
          return;
        }

        setMetrics(response);
        setErrorMessage(null);
        setStatus('online');
        setLastSuccessfulUpdate(new Date());
      } catch (error) {
        if (disposedRef.current) {
          return;
        }

        const normalized = normalizeError(error);
        if (normalized.kind === 'aborted') {
          return;
        }

        setErrorMessage(normalized.message);
        setStatus(resolveStatus(normalized));
      } finally {
        controllerRef.current = null;

        if (disposedRef.current) {
          return;
        }

        setIsRefreshing(false);
        timerRef.current = window.setTimeout(() => {
          void poll();
        }, refreshIntervalMs);
      }
    };

    void poll();

    return () => {
      disposedRef.current = true;
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      controllerRef.current?.abort();
    };
  }, []);

  const statusDetail =
    status === 'loading'
      ? 'Fetching the first live sample from the Monitoring Server.'
      : status === 'online'
        ? isRefreshing
          ? 'Refreshing metrics in the background.'
          : 'Connected to the Monitoring Server.'
        : errorMessage || 'Metrics are currently unavailable.';

  const cpuUsage = metrics?.cpu.usage_percent ?? null;
  const memoryUsage = metrics?.memory.percent ?? null;
  const diskUsage = metrics?.disk.percent ?? null;

  return (
    <main className="dashboard-shell">
      <section className="hero panel">
        <div className="hero__copy">
          <p className="hero__eyebrow">System Health Monitor</p>
          <h1>Monitoring dashboard</h1>
          <p className="hero__summary">
            Live metrics are fetched from the Monitoring Server at{' '}
            <code>{buildMetricsPath(serverId)}</code> and refreshed automatically every 5 seconds.
          </p>
        </div>
        <div className="hero__status">
          <StatusPill status={status} detail={statusDetail} />
          <div className="hero__meta">
            <span>
              <strong>Server name</strong>
              {serverName}
            </span>
            <span>
              <strong>Server ID</strong>
              {serverId}
            </span>
            <span>
              <strong>Last successful update</strong>
              {formatDateTime(lastSuccessfulUpdate)}
            </span>
          </div>
        </div>
      </section>

      <section className="overview-grid">
        <article className="panel overview-panel">
          <div className="section-heading">
            <div>
              <p className="section-heading__eyebrow">Server overview</p>
              <h2>Connection and update state</h2>
            </div>
            <span className="section-heading__badge">Auto-refresh {Math.round(refreshIntervalMs / 1000)}s</span>
          </div>
          <dl className="info-grid">
            <div>
              <dt>Server name</dt>
              <dd>{serverName}</dd>
            </div>
            <div>
              <dt>Server ID</dt>
              <dd>{serverId}</dd>
            </div>
            <div>
              <dt>Online status</dt>
              <dd>{status === 'online' ? 'Online' : status === 'loading' ? 'Loading' : 'Offline / Error'}</dd>
            </div>
            <div>
              <dt>Last successful update</dt>
              <dd>{formatDateTime(lastSuccessfulUpdate)}</dd>
            </div>
          </dl>
        </article>

        <article className="panel overview-panel">
          <div className="section-heading">
            <div>
              <p className="section-heading__eyebrow">System information</p>
              <h2>Host metadata</h2>
            </div>
            <span className="section-heading__badge">Live from Metrics Agent</span>
          </div>
          <dl className="info-grid info-grid--system">
            <div>
              <dt>Hostname</dt>
              <dd>{renderSystemValue(metrics?.system.hostname)}</dd>
            </div>
            <div>
              <dt>OS</dt>
              <dd>{renderSystemValue(metrics?.system.os_info)}</dd>
            </div>
            <div>
              <dt>Kernel version</dt>
              <dd>{renderSystemValue(metrics?.system.kernel_version)}</dd>
            </div>
            <div>
              <dt>Uptime</dt>
              <dd>{metrics ? formatUptime(metrics.system.uptime_seconds) : 'Waiting for first successful update'}</dd>
            </div>
          </dl>
        </article>
      </section>

      <section className="metrics-grid" aria-label="Live performance metrics">
        <MetricCard
          title="CPU usage"
          value={cpuUsage !== null ? formatPercent(cpuUsage) : 'Waiting for data'}
          subtitle={
            metrics
              ? `${metrics.cpu.core_count} physical cores · ${metrics.cpu.core_count_logical} logical cores`
              : 'CPU data will appear after the first successful update.'
          }
          percentage={cpuUsage ?? undefined}
          accent="var(--accent-cpu)"
          footer={metrics ? `Current frequency ${formatFrequency(metrics.cpu.frequency_current)}` : undefined}
        />

        <MetricCard
          title="Memory usage"
          value={metrics ? `${formatPercent(metrics.memory.percent)}` : 'Waiting for data'}
          subtitle={
            metrics
              ? `${formatBytes(metrics.memory.used)} used of ${formatBytes(metrics.memory.total)}`
              : 'Memory data will appear after the first successful update.'
          }
          percentage={memoryUsage ?? undefined}
          accent="var(--accent-memory)"
          footer={metrics ? `Available ${formatBytes(metrics.memory.available)}` : undefined}
        />

        <MetricCard
          title="Disk usage"
          value={metrics ? `${formatPercent(metrics.disk.percent)}` : 'Waiting for data'}
          subtitle={
            metrics
              ? `${formatBytes(metrics.disk.used)} used of ${formatBytes(metrics.disk.total)}`
              : 'Disk data will appear after the first successful update.'
          }
          percentage={diskUsage ?? undefined}
          accent="var(--accent-disk)"
          footer={metrics ? `Free ${formatBytes(metrics.disk.free)}` : undefined}
        />

        <article className="metric-card metric-card--network">
          <div className="section-heading section-heading--compact">
            <div>
              <p className="section-heading__eyebrow">Network</p>
              <h2>Traffic summary</h2>
            </div>
          </div>

          {metrics ? (
            <dl className="stat-grid">
              <div>
                <dt>Bytes sent</dt>
                <dd>{formatBytes(metrics.network.bytes_sent)}</dd>
              </div>
              <div>
                <dt>Bytes received</dt>
                <dd>{formatBytes(metrics.network.bytes_received)}</dd>
              </div>
              <div>
                <dt>Packets sent</dt>
                <dd>{formatInteger(metrics.network.packets_sent)}</dd>
              </div>
              <div>
                <dt>Packets received</dt>
                <dd>{formatInteger(metrics.network.packets_received)}</dd>
              </div>
            </dl>
          ) : (
            <p className="metric-card__subtitle">Network data will appear after the first successful update.</p>
          )}
        </article>
      </section>

      {status !== 'loading' && status !== 'online' ? (
        <section className={`panel alert alert--${status}`}>
          <p className="alert__title">Dashboard unavailable</p>
          <p className="alert__body">{statusDetail}</p>
        </section>
      ) : null}
    </main>
  );
}
