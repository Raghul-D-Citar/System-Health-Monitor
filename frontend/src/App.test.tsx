import { act, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import App from './App';

function createMetrics(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    cpu: {
      usage_percent: 25.5,
      core_count: 4,
      core_count_logical: 8,
      frequency_current: 2400,
      frequency_max: 3600,
      ...((overrides.cpu as object) || {}),
    },
    memory: {
      total: 17179869184,
      used: 8589934592,
      available: 8589934592,
      percent: 50,
      ...((overrides.memory as object) || {}),
    },
    disk: {
      total: 107374182400,
      used: 53687091200,
      free: 53687091200,
      percent: 50,
      ...((overrides.disk as object) || {}),
    },
    network: {
      bytes_sent: 1048576,
      bytes_received: 2097152,
      packets_sent: 10000,
      packets_received: 15000,
      ...((overrides.network as object) || {}),
    },
    system: {
      hostname: 'ubuntu-vm',
      os_info: 'Linux',
      kernel_version: '6.8.0-31-generic',
      uptime_seconds: 90061,
      ...((overrides.system as object) || {}),
    },
  };
}

function createResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: vi.fn().mockResolvedValue(body),
    text: vi.fn().mockResolvedValue(JSON.stringify(body)),
    clone() {
      return this;
    },
  } as unknown as Response;
}

function stubFetch(response: Response | Promise<Response> | Promise<never> | (() => Promise<Response>)) {
  const fetchMock = vi.fn(response instanceof Function ? response : () => Promise.resolve(response));
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

function flushMicrotasks() {
  return act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

describe('dashboard', () => {
  beforeEach(() => {
    vi.useRealTimers();
  });

  test('shows loading state before the first sample arrives', () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    expect(screen.getByText(/fetching the first live sample/i)).toBeInTheDocument();
    expect(screen.getAllByText('Loading').length).toBeGreaterThanOrEqual(2);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('renders live metrics and maps the response correctly', async () => {
    const fetchMock = stubFetch(createResponse(createMetrics()));

    render(<App />);
    await flushMicrotasks();

    expect(await screen.findByText(/connected to the monitoring server/i)).toBeInTheDocument();
    expect(screen.getAllByText('Ubuntu VM').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('ubuntu-1').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('25.5%')).toBeInTheDocument();
    expect(screen.getByText(/4 physical cores · 8 logical cores/i)).toBeInTheDocument();
    expect(screen.getByText(/Current frequency 2.40 GHz/i)).toBeInTheDocument();
    expect(screen.getByText(/8.0 GB used of 16 GB/i)).toBeInTheDocument();
    expect(screen.getByText(/Available 8.0 GB/i)).toBeInTheDocument();
    expect(screen.getAllByText('50.0%').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/1.0 MB/i)).toBeInTheDocument();
    expect(screen.getByText(/2.0 MB/i)).toBeInTheDocument();
    expect(screen.getByText('ubuntu-vm')).toBeInTheDocument();
    expect(screen.getByText('Linux')).toBeInTheDocument();
    expect(screen.getByText('6.8.0-31-generic')).toBeInTheDocument();
    expect(screen.getByText(/1d 1h 1m 1s/i)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith('/api/servers/ubuntu-1/metrics', expect.any(Object));
  });

  test('polls again automatically after the refresh interval', async () => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockResolvedValue(createResponse(createMetrics()));
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);
    await flushMicrotasks();

    expect(fetchMock).toHaveBeenCalledTimes(1);

    await act(async () => {
      vi.advanceTimersByTime(5000);
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  test('cleans up polling when unmounted', async () => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockResolvedValue(createResponse(createMetrics()));
    vi.stubGlobal('fetch', fetchMock);

    const { unmount } = render(<App />);
    await flushMicrotasks();

    expect(fetchMock).toHaveBeenCalledTimes(1);

    unmount();

    await act(async () => {
      vi.advanceTimersByTime(15000);
      await Promise.resolve();
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('shows offline state when the Monitoring Server cannot be reached', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    render(<App />);
    await flushMicrotasks();

    expect(await screen.findByText(/dashboard unavailable/i)).toBeInTheDocument();
    expect(screen.getByText('Offline')).toBeInTheDocument();
    expect(screen.getAllByText(/Monitoring Server is unavailable/i).length).toBeGreaterThanOrEqual(2);
  });

  test('shows offline state for a 503 response from the Monitoring Server', async () => {
    const response = createResponse(
      {
        status: 'error',
        detail: 'Cannot reach Metrics Agent at http://192.168.122.13:8001',
      },
      503,
    );
    const fetchMock = stubFetch(response);

    render(<App />);
    await flushMicrotasks();

    expect(await screen.findByText(/dashboard unavailable/i)).toBeInTheDocument();
    expect(screen.getByText('Offline')).toBeInTheDocument();
    expect(screen.getAllByText(/Cannot reach Metrics Agent/i).length).toBeGreaterThanOrEqual(2);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('shows an error state when the API payload is invalid', async () => {
    const response = createResponse({ hello: 'world' });
    const fetchMock = stubFetch(response);

    render(<App />);
    await flushMicrotasks();

    expect(await screen.findByText(/dashboard unavailable/i)).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getAllByText(/invalid or missing cpu metrics/i).length).toBeGreaterThanOrEqual(2);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
