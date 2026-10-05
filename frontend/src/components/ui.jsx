import { AlertCircle, CheckCircle2, Info, TriangleAlert } from 'lucide-react';

/* Centralized civic design-system primitives. All pages compose these —
   no per-page style duplication. Light theme only. */

export function Container({ children, narrow = false }) {
  return (
    <div className={`mx-auto w-full px-4 sm:px-6 ${narrow ? 'max-w-3xl' : 'max-w-[1200px]'}`}>
      {children}
    </div>
  );
}

export function PageHeader({ eyebrow, title, description }) {
  return (
    <div className="max-w-2xl">
      {eyebrow && (
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">{eyebrow}</p>
      )}
      <h1 className="mt-1.5 text-[28px] font-bold leading-tight tracking-tight text-ink md:text-[32px]">{title}</h1>
      {description && <p className="mt-2 text-base leading-relaxed text-ink-2">{description}</p>}
    </div>
  );
}

/* Touch-first: every button is at least 44px tall (primary actions 48px+). */
const buttonBase =
  'inline-flex min-h-[44px] items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60';

const buttonTones = {
  primary: 'bg-brand text-white hover:bg-brand-dark',
  secondary: 'border border-line bg-surface text-ink hover:border-muted hover:bg-surface-2',
  danger: 'bg-bad text-white hover:bg-[#b91c1c]',
  subtle: 'text-brand hover:bg-brand-tint',
};

export function Button({ variant = 'primary', className = '', ...props }) {
  return <button className={`${buttonBase} ${buttonTones[variant]} ${className}`} {...props} />;
}

export function Card({ title, action, children, className = '' }) {
  return (
    <section className={`rounded-xl border border-line bg-surface shadow-card ${className}`}>
      {title && (
        <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-3.5">
          <h2 className="text-[15px] font-semibold text-ink">{title}</h2>
          {action}
        </div>
      )}
      <div className="px-5 py-4">{children}</div>
    </section>
  );
}

export function Field({ label, htmlFor, hint, error, children }) {
  return (
    <div>
      <label htmlFor={htmlFor} className="block text-sm font-medium text-ink">
        {label}
      </label>
      {hint && <p className="mt-0.5 text-[13px] text-muted">{hint}</p>}
      <div className="mt-1.5">{children}</div>
      {error && (
        <p className="mt-1.5 text-[13px] font-medium text-bad" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

/* Mobile forms: full-width fields, min 44px tall, labels above (see Field). */
const inputCls =
  'w-full min-h-[44px] rounded-lg border border-line bg-surface px-3.5 py-2.5 text-base text-ink placeholder:text-muted/70 focus:border-brand focus:outline-none disabled:bg-surface-2 disabled:text-muted md:text-[15px]';

export function TextInput(props) {
  return <input {...props} className={`${inputCls} ${props.className || ''}`} />;
}

export function TextArea(props) {
  return <textarea {...props} className={`${inputCls} resize-y ${props.className || ''}`} />;
}

export function Select(props) {
  return <select {...props} className={`${inputCls} ${props.className || ''}`} />;
}

const alertTones = {
  info: { wrap: 'border-brand/30 bg-brand-tint text-ink', Icon: Info, icon: 'text-brand' },
  success: { wrap: 'border-ok/30 bg-ok-tint text-ink', Icon: CheckCircle2, icon: 'text-ok' },
  warning: { wrap: 'border-warn/40 bg-warn-tint text-ink', Icon: TriangleAlert, icon: 'text-warn' },
  error: { wrap: 'border-bad/30 bg-bad-tint text-ink', Icon: AlertCircle, icon: 'text-bad' },
};

export function Alert({ tone = 'info', children, className = '' }) {
  const t = alertTones[tone];
  const Icon = t.Icon;
  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      className={`flex items-start gap-2.5 rounded-lg border px-4 py-3 text-sm leading-relaxed ${t.wrap} ${className}`}
    >
      <Icon size={17} className={`mt-0.5 shrink-0 ${t.icon}`} aria-hidden />
      <div className="min-w-0">{children}</div>
    </div>
  );
}

export function EmptyState({ title, text, action }) {
  return (
    <div className="rounded-xl border border-line bg-surface px-6 py-10 text-center shadow-card">
      <p className="text-[15px] font-semibold text-ink">{title}</p>
      {text && <p className="mx-auto mt-1.5 max-w-md text-sm leading-relaxed text-ink-2">{text}</p>}
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </div>
  );
}

/* Professional data table: horizontal scroll on small screens, compact rows. */
export function Table({ children, minWidth = 720 }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-line bg-surface shadow-card">
      <table className="w-full text-left text-sm" style={{ minWidth }}>
        {children}
      </table>
    </div>
  );
}

export function Th({ children, className = '' }) {
  return (
    <th className={`border-b border-line bg-surface-2/60 px-3.5 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted ${className}`}>
      {children}
    </th>
  );
}

export function Td({ children, className = '' }) {
  return <td className={`border-b border-line/70 px-3.5 py-2.5 align-top text-ink-2 last:border-b-0 ${className}`}>{children}</td>;
}

const badgeTones = {
  slate: 'border-line bg-surface-2 text-ink-2',
  blue: 'border-brand/30 bg-brand-tint text-brand-dark',
  green: 'border-ok/30 bg-ok-tint text-ok',
  amber: 'border-warn/40 bg-warn-tint text-[#92400e]',
  red: 'border-bad/30 bg-bad-tint text-bad',
};

/** Small status badge — always text + tinted indicator, never color alone. */
export function Badge({ tone = 'slate', children, className = '' }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${badgeTones[tone]} ${className}`}>
      {children}
    </span>
  );
}

export function RiskBadge({ level }) {
  const map = {
    HIGH: { tone: 'red', label: 'High risk' },
    MEDIUM: { tone: 'amber', label: 'Medium risk' },
    LOW: { tone: 'green', label: 'Low risk' },
  };
  const m = map[level] || map.MEDIUM;
  return <Badge tone={m.tone}>{m.label}</Badge>;
}

/** Mobile report card (admin lists): stacked label/value rows + action.
 * Desktop keeps real tables; this is the <md presentation of the same data. */
export function ReportCard({ title, risk, rows, action }) {
  return (
    <article className="rounded-xl border border-line bg-surface p-4 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-[15px] font-bold tracking-tight text-ink">{title}</p>
        {risk}
      </div>
      <dl className="mt-3 space-y-1.5">
        {rows.map(([label, value]) => (
          <div key={label} className="flex items-baseline justify-between gap-3 text-sm">
            <dt className="shrink-0 text-muted">{label}:</dt>
            <dd className="min-w-0 text-right font-medium text-ink">{value}</dd>
          </div>
        ))}
      </dl>
      {action && <div className="mt-3">{action}</div>}
    </article>
  );
}

/** Restrained key figure: label + value, no oversized colorful cards. */
export function Stat({ label, value, hint }) {
  return (
    <div className="rounded-xl border border-line bg-surface px-4 py-3.5 shadow-card">
      <p className="text-[13px] font-medium text-muted">{label}</p>
      <p className="mt-1 truncate text-xl font-bold text-ink" title={typeof value === 'string' ? value : undefined}>
        {value}
      </p>
      {hint && <p className="mt-0.5 text-xs text-muted">{hint}</p>}
    </div>
  );
}
