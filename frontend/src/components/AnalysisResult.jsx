import { useNavigate } from 'react-router-dom';
import IndicatorCard from './IndicatorCard';
import RiskBadge from './RiskBadge';
import { Alert, Button, Card } from './ui';

/** Clean result card: badge + category first, explanation prominent,
 * numeric score secondary. No gauges, no certainty language. */
export default function AnalysisResult({ result, sourceText, onReset }) {
  const navigate = useNavigate();
  const pct = Math.round((result.model_confidence || 0) * 100);
  const border =
    result.risk_level === 'HIGH'
      ? 'border-l-bad'
      : result.risk_level === 'LOW'
        ? 'border-l-ok'
        : 'border-l-warn';

  return (
    <section aria-live="polite" className={`mt-6 rounded-xl border border-line border-l-4 bg-surface shadow-card ${border}`}>
      <div className="border-b border-line px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Analysis result</p>
        <div className="mt-2.5">
          <RiskBadge level={result.risk_level} score={result.risk_score} />
        </div>
        <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-[13px] text-muted">Category</dt>
            <dd className="mt-0.5 font-semibold text-ink">
              {result.category_label}
              <span className="ml-2 font-mono text-xs font-normal text-muted">{result.category}</span>
            </dd>
          </div>
          <div>
            <dt className="text-[13px] text-muted">Model signal</dt>
            <dd className="mt-0.5 text-ink-2" title="Classifier confidence — not the probability of actual fraud">
              {pct}% · {result.model_version}
              {!result.ml_available && ' (rule fallback)'}
            </dd>
          </div>
        </dl>
      </div>

      <div className="space-y-4 px-5 py-5">
        <div>
          <h3 className="text-[15px] font-semibold text-ink">
            Why this was flagged ({result.indicators.length} indicator{result.indicators.length === 1 ? '' : 's'})
          </h3>
          {result.indicators.length === 0 ? (
            <p className="mt-2 text-sm text-ink-2">No common scam indicators were found in this message.</p>
          ) : (
            <ul className="mt-2.5 space-y-2">
              {result.indicators.map((i) => (
                <IndicatorCard key={i.code} indicator={i} />
              ))}
            </ul>
          )}
        </div>

        {result.urls && result.urls.length > 0 && (
          <div>
            <h3 className="text-[15px] font-semibold text-ink">
              Links found ({result.urls.length})
            </h3>
            <div className="mt-2.5 space-y-3">
              {result.urls.map((u) => (
                <div key={u.url} className="rounded-lg border border-line bg-surface-2/50 p-3.5">
                  <p className="break-all font-mono text-xs text-ink-2">{u.url}</p>
                  <p className="mt-1.5 text-xs font-semibold text-ink">
                    {u.risk_level}
                    <span className="ml-2 font-normal text-muted">score {u.risk_score}/100 · checked statically, never visited</span>
                  </p>
                  {u.signals.length === 0 ? (
                    <p className="mt-1 text-xs text-muted">No major structural indicators.</p>
                  ) : (
                    <ul className="mt-2 space-y-2">
                      {u.signals.map((s) => (
                        <IndicatorCard key={s.code} indicator={s} />
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <Card title="Explanation">
          <p className="text-sm leading-relaxed text-ink">{result.explanation}</p>
        </Card>

        <Alert tone="info">
          <span className="font-semibold">Recommended action: </span>
          {result.recommendation}
        </Alert>

        <details className="rounded-lg border border-line bg-surface-2/50 px-4 py-3">
          <summary className="cursor-pointer text-sm font-semibold text-ink">
            How we assessed this
          </summary>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-[13px] leading-relaxed text-ink-2">
            <li>
              Classification ({result.model_version})
              {result.ml_available ? ' was applied' : ' was unavailable, so rule signals were used instead'}.
            </li>
            <li>Message signals checked — {result.indicators.length} indicator(s) found.</li>
            <li>Links checked statically (never visited) — {result.urls ? result.urls.length : 0} found.</li>
          </ul>
          <p className="mt-2 text-xs leading-relaxed text-muted">
            The model signal reflects the classifier’s own scoring on small
            development data — it is not the probability that this message is
            actually fraud. Several scam indicators were detected; treat this
            as guidance, not certainty.
          </p>
        </details>

        <Alert tone="warning">
          <span className="font-semibold">Important limitation: </span>
          {result.disclaimer}
        </Alert>

        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <Button
            variant="secondary"
            className="w-full sm:w-auto"
            onClick={() => navigate('/report', {
              state: {
                fromAnalysis: true,
                category: result.category,
                contentType: 'message',
                content: sourceText || '',
              },
            })}
          >
            Report this message
          </Button>
          <Button onClick={onReset} className="h-12 w-full text-[15px] sm:h-11 sm:w-auto">
            Analyze another
          </Button>
        </div>
      </div>
    </section>
  );
}
