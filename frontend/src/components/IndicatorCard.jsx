const dot = {
  high: 'bg-bad',
  medium: 'bg-warn',
  low: 'bg-brand',
};

export default function IndicatorCard({ indicator }) {
  return (
    <li className="flex gap-3 rounded-lg border border-line bg-surface-2/50 px-3.5 py-3">
      <span
        className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${dot[indicator.severity] || dot.low}`}
        aria-hidden
      />
      <div className="min-w-0">
        <p className="text-sm font-semibold text-ink">
          {indicator.title}
          <span className="ml-2 rounded border border-line bg-surface px-1.5 py-0.5 align-middle text-[10px] font-semibold uppercase tracking-wider text-muted">
            {indicator.severity}
          </span>
        </p>
        <p className="mt-1 text-[13px] leading-relaxed text-ink-2">{indicator.description}</p>
      </div>
    </li>
  );
}
