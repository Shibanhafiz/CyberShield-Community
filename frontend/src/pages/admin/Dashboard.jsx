import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import LoadingState from '../../components/LoadingState';
import StatCard from '../../components/StatCard';
import { Alert, Button, Card } from '../../components/ui';
import { adminOverview } from '../../api';

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    adminOverview()
      .then((d) => { if (mounted) setData(d); })
      .catch(() => { if (mounted) setError('Dashboard data temporarily unavailable.'); });
    return () => { mounted = false; };
  }, []);

  if (error) {
    return <Alert tone="error">{error}</Alert>;
  }

  if (!data) return <LoadingState label="Loading overview…" />;

  const empty = data.total_reports === 0 && data.quiz_attempts === 0;

  return (
    <div>
      <h1 className="text-xl font-bold tracking-tight text-ink">Overview</h1>
      <p className="mt-1 text-[13px] text-muted">Real database values — nothing estimated.</p>
      {empty && (
        <Alert tone="info" className="mt-4">
          Not enough data yet. Reports, quiz attempts and sessions will appear here.
        </Alert>
      )}
      <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Total reports" value={data.total_reports} />
        <StatCard label="Pending review" value={data.pending_reports} />
        <StatCard label="Reviewed" value={data.reviewed_reports} />
        <StatCard label="Archived" value={data.archived_reports} />
        <StatCard label="High-risk" value={data.high_risk_reports} />
        <StatCard label="Awareness sessions" value={data.awareness_sessions_completed} />
        <StatCard label="Quiz attempts" value={data.quiz_attempts} />
        <StatCard label="Feedback" value={data.feedback_count} />
      </div>
      <Card title="Moderation queue" className="mt-4">
        <p className="text-sm text-ink-2">
          {data.pending_reports === 0
            ? 'No reports are waiting for review.'
            : `${data.pending_reports} report${data.pending_reports === 1 ? '' : 's'} waiting for review.`}
        </p>
        <div className="mt-3 flex flex-wrap gap-3">
          <Link to="/admin/reports">
            <Button>Review reports</Button>
          </Link>
          <Link to="/admin/analytics">
            <Button variant="secondary">View analytics</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
