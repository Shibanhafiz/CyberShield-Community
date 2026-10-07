import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import LoadingState from '../components/LoadingState';
import PageMeta from '../components/PageMeta';
import StatCard from '../components/StatCard';
import { Alert, Button, Container, EmptyState, PageHeader } from '../components/ui';
import { getImpactSummary } from '../api';

export default function Impact() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    getImpactSummary()
      .then((d) => { if (mounted) setData(d); })
      .catch(() => { if (mounted) setError('Impact data is temporarily unavailable.'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <Container narrow>
        <LoadingState label="Loading impact data…" />
      </Container>
    );
  }

  if (error) {
    return (
      <Container narrow>
        <Alert tone="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <PageMeta
        title="Community Impact"
        description="Real aggregated awareness metrics from this platform: quizzes, sessions and score changes. Nothing estimated."
      />
      <PageHeader
        eyebrow="Impact"
        title="Community impact"
        description="Real aggregated awareness metrics from this platform's database — nothing estimated, nothing imported."
      />

      {!data.has_data ? (
        <div className="mt-6">
          <EmptyState
            title="Not enough field data yet."
            text="Awareness sessions and quizzes completed here will appear as public, anonymized aggregates."
            action={(
              <span className="flex flex-wrap justify-center gap-3">
                <Link to="/awareness" className="inline-flex h-10 items-center rounded-lg bg-brand px-5 text-sm font-semibold text-white hover:bg-brand-dark">
                  Start assessment
                </Link>
                <Link to="/quiz" className="inline-flex h-10 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
                  Take the quiz
                </Link>
              </span>
            )}
          />
        </div>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatCard label="Quizzes completed" value={data.quizzes_completed} />
            <StatCard label="Awareness sessions" value={data.awareness_sessions_completed} />
            <StatCard
              label="Avg score change"
              value={data.avg_score_change == null ? '—' : `${data.avg_score_change >= 0 ? '+' : ''}${data.avg_score_change}`}
            />
            <StatCard label="Most difficult topic" value={data.most_difficult_category || '—'} small />
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            <StatCard label="Avg before score" value={data.avg_before_score ?? '—'} />
            <StatCard label="Avg after score" value={data.avg_after_score ?? '—'} />
            <StatCard label="Most reviewed topic" value={data.most_reviewed_topic || '—'} small />
          </div>
          <Alert tone="info" className="mt-6">
            These measure quiz performance on this platform only. They do not prove
            anyone is protected from scams — awareness helps, caution protects.
          </Alert>
        </>
      )}
    </Container>
  );
}
