import type { DashboardStatus } from '../types';

interface StatusPillProps {
  status: DashboardStatus;
  detail?: string;
}

const LABELS: Record<DashboardStatus, string> = {
  loading: 'Loading',
  online: 'Online',
  offline: 'Offline',
  error: 'Error',
};

export function StatusPill({ status, detail }: StatusPillProps) {
  return (
    <div className={`status-pill status-pill--${status}`} aria-live="polite">
      <span className="status-pill__dot" aria-hidden="true" />
      <div className="status-pill__content">
        <strong>{LABELS[status]}</strong>
        {detail ? <span>{detail}</span> : null}
      </div>
    </div>
  );
}
