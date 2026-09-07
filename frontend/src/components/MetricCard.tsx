interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  percentage?: number;
  accent: string;
  footer?: string;
}

function clampPercentage(value: number): number {
  return Math.max(0, Math.min(100, value));
}

export function MetricCard({
  title,
  value,
  subtitle,
  percentage,
  accent,
  footer,
}: MetricCardProps) {
  const hasPercentage = typeof percentage === 'number' && Number.isFinite(percentage);
  const progress = hasPercentage ? clampPercentage(percentage) : 0;

  return (
    <article className="metric-card">
      <header className="metric-card__header">
        <div>
          <p className="metric-card__eyebrow">{title}</p>
          <h3>{value}</h3>
        </div>
        {hasPercentage ? (
          <div
            className="metric-card__ring"
            style={{
              ['--metric-progress' as never]: `${progress}%`,
              ['--metric-accent' as never]: accent,
            }}
            aria-label={`${title} usage ${progress.toFixed(1)} percent`}
            role="img"
          >
            <span>{progress.toFixed(0)}%</span>
          </div>
        ) : null}
      </header>
      {subtitle ? <p className="metric-card__subtitle">{subtitle}</p> : null}
      {hasPercentage ? (
        <div className="metric-card__bar" aria-hidden="true">
          <span
            className="metric-card__bar-fill"
            style={{
              ['--metric-progress' as never]: `${progress}%`,
              ['--metric-accent' as never]: accent,
            }}
          />
        </div>
      ) : null}
      {footer ? <p className="metric-card__footer">{footer}</p> : null}
    </article>
  );
}
