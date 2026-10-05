import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import LoadingState from '../../components/LoadingState';
import { Alert, Badge, Button, Card } from '../../components/ui';
import { adminReport, adminUpdateReportStatus } from '../../api';

const STATUSES = ['PENDING', 'REVIEWED', 'ARCHIVED'];

function Row({ label, children }) {
  return (
    <div className="flex justify-between gap-3 border-b border-line/70 py-1.5 text-sm last:border-b-0">
      <dt className="text-muted">{label}</dt>
      <dd className="text-right font-medium text-ink">{children}</dd>
    </div>
  );
}

export default function ReportDetail() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [target, setTarget] = useState('');
  const [confirming, setConfirming] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState('');

  useEffect(() => {
    let mounted = true;
    adminReport(id)
      .then((d) => { if (mounted) setReport(d); })
      .catch(() => { if (mounted) setError('Report not found or temporarily unavailable.'); });
    return () => { mounted = false; };
  }, [id]);

  async function applyStatus() {
    setSaving(true);
    setNotice('');
    try {
      const res = await adminUpdateReportStatus(id, target);
      setReport((r) => ({ ...r, status: res.status }));
      setConfirming(false);
      setTarget('');
      setNotice(`Status changed to ${res.status}. Change recorded in the audit log.`);
    } catch {
      setNotice('Could not update status. Please try again.');
    } finally {
      setSaving(false);
    }
  }

  if (error) {
    return (
      <div>
        <Alert tone="error">{error}</Alert>
        <Link to="/admin/reports" className="mt-4 inline-block text-sm font-semibold text-brand-dark hover:underline">← Back to reports</Link>
      </div>
    );
  }

  if (!report) return <LoadingState label="Loading report…" />;

  return (
    <div>
      <Link to="/admin/reports" className="text-[13px] font-medium text-muted hover:text-ink">← Back to reports</Link>
      <div className="mt-2 flex flex-wrap items-center gap-3">
        <h1 className="font-mono text-lg font-bold text-ink">{report.id}</h1>
        <Badge tone={report.status === 'PENDING' ? 'amber' : report.status === 'REVIEWED' ? 'green' : 'slate'}>
          {report.status}
        </Badge>
      </div>
      <p className="mt-1 max-w-2xl text-[13px] text-muted">
        Automated analysis indicates several suspicious signals — this is an indicative assessment, not a confirmed scam finding.
      </p>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <Card title="Community-submitted information">
          <dl>
            <Row label="Category">{report.category}</Row>
            <Row label="Content type">{report.content_type}</Row>
            <Row label="Area">{report.approximate_area || '—'}</Row>
            <Row label="Submitted">{new Date(report.reported_at).toLocaleString()}</Row>
            <Row label="Duplicate signals">
              {report.duplicate_count > 0 ? `Possible duplicate reports: ${report.duplicate_count}` : 'None detected'}
            </Row>
          </dl>
        </Card>
        <Card title="Automated analysis (indicative)">
          <dl>
            <Row label="Risk level">{report.risk_level || '—'}</Row>
            <Row label="Times reported">{report.report_count}</Row>
          </dl>
          {report.description && (
            <p className="mt-2 text-[13px] text-ink-2"><span className="font-semibold text-ink">Reporter note: </span>{report.description}</p>
          )}
        </Card>
      </div>

      <Alert tone="warning" className="mt-4">
        <span className="font-semibold">Sanitized submitted content:</span>
        <span className="mt-1 block whitespace-pre-wrap break-words">{report.sanitized_content}</span>
        <span className="mt-1 block text-xs">Community submissions may contain sensitive information. Handle responsibly.</span>
      </Alert>

      {report.duplicate_ids.length > 0 && (
        <Card title="Related reports (same content fingerprint)" className="mt-4">
          <ul className="space-y-1 font-mono text-[13px]">
            {report.duplicate_ids.map((d) => (
              <li key={d}><Link to={`/admin/reports/${d}`} className="text-brand-dark hover:underline">{d}</Link></li>
            ))}
          </ul>
          <p className="mt-2 text-[13px] text-muted">Records are kept for data integrity — duplicates are linked, never auto-deleted.</p>
        </Card>
      )}

      <Card title="Moderation action" className="mt-4">
        {!confirming ? (
          <div className="flex flex-wrap gap-2">
            {STATUSES.filter((s) => s !== report.status).map((s) => (
              <Button
                key={s}
                variant="secondary"
                onClick={() => { setTarget(s); setConfirming(true); }}
              >
                Mark {s.charAt(0) + s.slice(1).toLowerCase()}
              </Button>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-warn/50 bg-warn-tint p-4 text-sm">
            <p className="text-ink">
              Change status from <span className="font-semibold">{report.status}</span> to{' '}
              <span className="font-semibold">{target}</span>? This will be audit-logged.
            </p>
            <div className="mt-3 flex gap-2">
              <Button onClick={applyStatus} disabled={saving}>
                {saving ? 'Saving…' : 'Confirm change'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => { setConfirming(false); setTarget(''); }}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
        {notice && <p className="mt-2 text-[13px] text-ink-2" role="status">{notice}</p>}
      </Card>
    </div>
  );
}
