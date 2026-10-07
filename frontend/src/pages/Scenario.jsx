import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, CheckCircle2, XCircle } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import PageMeta from '../components/PageMeta';
import { Alert, Button, Card, Container } from '../components/ui';
import { answerScenario, getScenario, getScenarios } from '../api';

export default function Scenario() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [scenario, setScenario] = useState(null);
  const [nextId, setNextId] = useState(null);
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setSelected(null);
    setResult(null);
    setError('');
    Promise.all([getScenario(id), getScenarios()])
      .then(([s, list]) => {
        if (!mounted) return;
        setScenario(s);
        const idx = list.findIndex((x) => x.scenario_id === id);
        setNextId(idx >= 0 && idx < list.length - 1 ? list[idx + 1].scenario_id : null);
      })
      .catch(() => {
        if (mounted) setError('Could not load this scenario. Please try again.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [id]);

  async function choose(i) {
    if (result) return;
    setSelected(i);
    try {
      setResult(await answerScenario(id, i));
    } catch {
      setResult({ error: true });
    }
  }

  if (loading) {
    return (
      <Container narrow>
        <LoadingState label="Loading scenario…" />
      </Container>
    );
  }

  if (error || !scenario) {
    return (
      <Container narrow>
        <Alert tone="error">{error || 'Scenario not found.'}</Alert>
        <Link to="/learn" className="mt-4 inline-block text-sm font-semibold text-brand-dark hover:underline">
          ← Back to Learning Center
        </Link>
      </Container>
    );
  }

  return (
    <Container narrow>
      <PageMeta
        title="Practice Scenario"
        description="Decide what to do about a fictional scam message, then see why the safe choice is safe."
      />
      <Link to="/learn" className="inline-flex items-center gap-1.5 text-[13px] font-medium text-muted hover:text-ink">
        <ArrowLeft size={14} aria-hidden /> Back to Learning Center
      </Link>

      <p className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-muted">
        Practice scenario · {scenario.category} · {scenario.difficulty}
      </p>
      <h1 className="mt-1 text-2xl font-bold tracking-tight text-ink">{scenario.title}</h1>

      <Card className="mt-4" title="You receive this message">
        <p className="text-[13px] text-muted">Fictional example — do not act on it for real.</p>
        <p className="mt-2 text-[15px] leading-relaxed text-ink">{scenario.message}</p>
      </Card>

      <h2 className="mt-6 text-lg font-bold text-ink">What would you do?</h2>
      <div className="mt-3 space-y-2" role="group" aria-label="Your response choices">
        {scenario.choices.map((c, i) => {
          const isSel = selected === i;
          let cls = 'border-line bg-surface hover:border-brand/60';
          if (result && !result.error) {
            if (c === result.correct_action) cls = 'border-ok/60 bg-ok-tint';
            else if (isSel) cls = 'border-bad/60 bg-bad-tint';
          }
          return (
            <button
              key={i}
              onClick={() => choose(i)}
              disabled={!!result}
              className={`min-h-[48px] w-full rounded-xl border px-4 py-3 text-left text-[15px] transition-colors disabled:cursor-default ${cls}`}
            >
              <span className="mr-2 font-bold text-brand-dark" aria-hidden>{String.fromCharCode(65 + i)}.</span>
              {c}
            </button>
          );
        })}
      </div>

      {result && !result.error && (
        <div className={`mt-4 rounded-xl border p-5 ${result.safe_choice ? 'border-ok/40 bg-ok-tint' : 'border-warn/50 bg-warn-tint'}`}>
          <p className={`flex items-center gap-2 font-semibold ${result.safe_choice ? 'text-ok' : 'text-[#92400e]'}`}>
            {result.safe_choice ? <CheckCircle2 size={18} aria-hidden /> : <XCircle size={18} aria-hidden />}
            {result.safe_choice ? 'Safe choice — well done.' : 'Unsafe choice — here is why.'}
          </p>
          <p className="mt-2 text-sm leading-relaxed text-ink">{result.explanation}</p>
          <div className="mt-3 text-sm">
            <p className="font-semibold text-ink">Warning signals in this message:</p>
            <ul className="mt-1 list-disc space-y-1 pl-5 text-ink-2">
              {result.warning_signals.map((w) => <li key={w}>{w}</li>)}
            </ul>
          </div>
          <p className="mt-3 rounded-lg border border-brand/30 bg-brand-tint p-3 text-sm text-ink">
            <span className="font-semibold">Recommended action: </span>
            {result.correct_action}
          </p>
          {nextId && (
            <Button onClick={() => navigate(`/learn/scenario/${nextId}`)} className="mt-4">
              Next scenario <ArrowRight size={15} aria-hidden />
            </Button>
          )}
        </div>
      )}
      {result && result.error && (
        <p className="mt-4 text-sm font-medium text-bad">Could not check your answer. Please try again.</p>
      )}
    </Container>
  );
}
