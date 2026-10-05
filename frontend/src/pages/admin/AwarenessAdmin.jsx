import { useEffect, useState } from 'react';
import LoadingState from '../../components/LoadingState';
import StatCard from '../../components/StatCard';
import { Alert, Card } from '../../components/ui';
import { adminAwarenessSummary } from '../../api';

export default function AwarenessAdmin() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    adminAwarenessSummary()
      .then((d) => { if (mounted) setData(d); })
      .catch(() => { if (mounted) setError('Awareness metrics temporarily unavailable.'); });
    return () => { mounted = false; };
  }, []);

  if (error) {
    return <Alert tone="error">{error}</Alert>;
  }

  if (!data) return <LoadingState label="Loading awareness metrics…" />;

  const empty = !data.has_data;

  return (
    <div>
      <h1 className="text-xl font-bold tracking-tight text-ink">Awareness impact</h1>
      <p className="mt-1 max-w-2xl text-[13px] leading-relaxed text-muted">
        Descriptive project metrics only — average quiz-score movement, never a claim that scams were prevented.
      </p>
      {empty && (
        <Alert tone="info" className="mt-4">
          Not enough data yet. Completed before/after sessions will appear here.
        </Alert>
      )}
      <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Sessions started" value={data.total_sessions_started} />
        <StatCard label="Completed before" value={data.completed_before} />
        <StatCard label="Completed after" value={data.completed_after} />
        <StatCard label="Full sessions" value={data.awareness_sessions_completed} />
        <StatCard label="Avg before" value={data.avg_before_score ?? '—'} />
        <StatCard label="Avg after" value={data.avg_after_score ?? '—'} />
        <StatCard
          label="Avg change"
          value={data.avg_score_change == null ? '—' : `${data.avg_score_change >= 0 ? '+' : ''}${data.avg_score_change}`}
        />
        <StatCard label="Quiz attempts" value={data.quizzes_completed} />
      </div>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <StatCard label="Most difficult category" value={data.most_difficult_category || '—'} small />
        <StatCard label="Most reviewed topic" value={data.most_reviewed_topic || '—'} small />
      </div>
      <Card title="How to read this" className="mt-4">
        <p className="text-sm text-ink-2">
          Average awareness quiz score changed by {data.avg_score_change == null ? '—' : `${data.avg_score_change >= 0 ? '+' : ''}${data.avg_score_change} points`}.
        </p>
        <p className="mt-1 text-[13px] text-muted">
          Interpret alongside field notes in docs/field-study — numbers alone do not prove real-world protection.
        </p>
      </Card>
    </div>
  );
}
