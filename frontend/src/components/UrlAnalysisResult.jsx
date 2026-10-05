import { useNavigate } from 'react-router-dom';
import IndicatorCard from './IndicatorCard';
import RiskBadge from './RiskBadge';
import { Alert, Button, Card } from './ui';

function Detail({ label, value }) {
  return (
    <div className="rounded-lg border border-line bg-surface-2/50 px-3 py-2">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">{label}</p>
      <p className="mt-0.5 break-all font-mono text-xs text-ink">{value}</p>
    </div>
  );
}

export default function UrlAnalysisResult({ result, onReset }) {
  const navigate = useNavigate();
  const t = result.technical_details;
  const border =
    result.risk_level === 'HIGH'
      ? 'border-l-bad'
      : result.risk_level === 'LOW'
        ? 'border-l-ok'
        : 'border-l-warn';

  return (
    <section aria-live="polite" className={`mt-6 rounded-xl border border-line border-l-4 bg-surface shadow-card ${border}`}>
      <div className="border-b border-line px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">URL analysis</p>
        <p className="mt-2 break-all font-mono text-sm text-ink">{result.url}</p>
        <div className="mt-2.5">
          <RiskBadge level={result.risk_level} score={result.risk_score} />
        </div>
      </div>

      <div className="space-y-4 px-5 py-5">
        <div>
          <h3 className="text-[15px] font-semibold text-ink">
            Indicators detected ({result.signals.length})
          </h3>
          {result.signals.length === 0 ? (
            <p className="mt-2 text-sm text-ink-2">No major structural indicators were detected in this URL.</p>
          ) : (
            <ul className="mt-2.5 space-y-2">
              {result.signals.map((s) => (
                <IndicatorCard key={s.code} indicator={s} />
              ))}
            </ul>
          )}
        </div>

        <Card title="Technical details">
          <div className="grid gap-2 sm:grid-cols-2">
            <Detail label="Domain" value={t.domain} />
            <Detail label="Subdomain" value={t.subdomains.length ? t.subdomains.join('.') : '—'} />
            <Detail label="HTTPS" value={t.uses_https ? 'Yes (does not prove safety)' : 'No'} />
            <Detail label="IP address" value={t.uses_ip_address ? `Yes${t.is_private_ip ? ' (private/loopback)' : ''}` : 'No'} />
            <Detail label="Port" value={t.port ?? 'default'} />
            <Detail label="URL length" value={String(t.url_length)} />
          </div>
          {!result.reputation.available && (
            <p className="mt-2 text-xs text-muted">
              Threat-intelligence check: unavailable ({result.reputation.reason})
            </p>
          )}
        </Card>

        <Card title="Explanation">
          <p className="text-sm leading-relaxed text-ink">{result.explanation}</p>
          <p className="mt-2 text-sm leading-relaxed text-ink-2">{result.recommendation}</p>
        </Card>

        <Alert tone="warning">
          These indicators do not by themselves prove that a website is
          malicious. {result.disclaimer}
        </Alert>

        <div className="flex flex-wrap gap-3">
          <Button
            variant="secondary"
            onClick={() => navigate('/report', {
              state: {
                fromAnalysis: true,
                category: 'PHISHING',
                contentType: 'url',
                content: result.url,
              },
            })}
          >
            Report this link
          </Button>
          <Button onClick={onReset}>Analyze another</Button>
        </div>
      </div>
    </section>
  );
}
