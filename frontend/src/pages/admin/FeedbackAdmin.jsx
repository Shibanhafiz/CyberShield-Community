import { useEffect, useState } from 'react';
import LoadingState from '../../components/LoadingState';
import StatCard from '../../components/StatCard';
import { Alert, Card, EmptyState } from '../../components/ui';
import { adminFeedback, adminFeedbackStats } from '../../api';

export default function FeedbackAdmin() {
  const [stats, setStats] = useState(null);
  const [rows, setRows] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([adminFeedbackStats(), adminFeedback()])
      .then(([s, r]) => {
        if (mounted) {
          setStats(s);
          setRows(r);
        }
      })
      .catch(() => { if (mounted) setError('Feedback data temporarily unavailable.'); });
    return () => { mounted = false; };
  }, []);

  if (error) {
    return <Alert tone="error">{error}</Alert>;
  }

  if (!stats) return <LoadingState label="Loading feedback…" />;

  return (
    <div>
      <h1 className="text-xl font-bold tracking-tight text-ink">Field-study feedback</h1>
      <p className="mt-1 text-[13px] text-muted">Anonymous submissions. Counts and averages only — no automated theme invention.</p>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatCard label="Total submissions" value={stats.total} />
        <StatCard label="Average rating" value={stats.average_rating == null ? '—' : `${stats.average_rating} / 5`} />
        <StatCard label="Topics covered" value={stats.by_topic.length} />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card title="By topic">
          {stats.by_topic.length === 0 ? (
            <p className="text-[13px] text-muted">Not enough data yet.</p>
          ) : (
            <ul className="space-y-1.5 text-sm">
              {stats.by_topic.map((t) => (
                <li key={t.topic} className="flex items-center justify-between gap-3 border-b border-line/70 py-1.5 text-ink-2 last:border-b-0">
                  <span className="truncate">{t.topic}</span>
                  <span className="shrink-0 font-semibold text-ink">{t.count} × · ★ {t.avg_rating}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card title="By participant category">
          {stats.by_category.length === 0 ? (
            <p className="text-[13px] text-muted">Not enough data yet.</p>
          ) : (
            <ul className="space-y-1.5 text-sm">
              {stats.by_category.map((c) => (
                <li key={c.category} className="flex items-center justify-between gap-3 border-b border-line/70 py-1.5 text-ink-2 last:border-b-0">
                  <span className="truncate">{c.category}</span>
                  <span className="shrink-0 font-semibold text-ink">{c.count}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card title="Recent submissions" className="mt-4">
        {rows.length === 0 ? (
          <EmptyState title="No feedback yet." text="Anonymous responses will appear here once submitted." />
        ) : (
          <ul className="space-y-3">
            {rows.map((r) => (
              <li key={r.id} className="rounded-lg border border-line bg-surface-2/50 p-3.5 text-[13px]">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-semibold text-ink">{r.topic}</span>
                  <span className="font-semibold text-[#92400e]">★ {r.rating}/5</span>
                </div>
                {r.feedback && <p className="mt-1.5 leading-relaxed text-ink-2">{r.feedback}</p>}
                <p className="mt-1.5 text-muted">
                  {[r.participant_category, r.broad_locality].filter(Boolean).join(' · ') || 'Anonymous'}
                  {' · '}{new Date(r.created_at).toLocaleDateString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
