import { useState } from 'react';
import { Download } from 'lucide-react';
import { Alert, Button, Card } from '../../components/ui';
import { adminExport } from '../../api';

const EXPORTS = [
  { name: 'reports', title: 'Community reports', text: 'Anonymized reports: category, type, risk, area, status, sanitized content.' },
  { name: 'awareness', title: 'Awareness & quiz activity', text: 'Sessions with before/after scores and quiz attempts with category tallies.' },
  { name: 'feedback', title: 'Field-study feedback', text: 'Anonymous feedback: topic, rating, category, locality.' },
];

export default function Exports() {
  const [busy, setBusy] = useState(null);
  const [notice, setNotice] = useState('');
  const [failed, setFailed] = useState(false);

  async function download(name) {
    setBusy(name);
    setNotice('');
    setFailed(false);
    try {
      const res = await adminExport(name);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `${name}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setNotice(`${name}.csv downloaded. This export was recorded in the audit log.`);
    } catch {
      setFailed(true);
      setNotice('Export failed. Please try again.');
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <h1 className="text-xl font-bold tracking-tight text-ink">Data exports</h1>
      <p className="mt-1 max-w-2xl text-[13px] leading-relaxed text-muted">
        CSV exports of anonymized project data. Community submissions may contain sensitive
        information — handle exported data responsibly. Every export is audit-logged.
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        {EXPORTS.map((e) => (
          <Card key={e.name} title={e.title}>
            <p className="min-h-[3.5rem] text-[13px] leading-relaxed text-ink-2">{e.text}</p>
            <Button
              onClick={() => download(e.name)}
              disabled={busy !== null}
              className="mt-3 h-9 text-[13px]"
            >
              <Download size={14} aria-hidden /> {busy === e.name ? 'Preparing…' : `Export ${e.name}.csv`}
            </Button>
          </Card>
        ))}
      </div>
      {notice && <div className="mt-3"><Alert tone={failed ? 'error' : 'success'}>{notice}</Alert></div>}
    </div>
  );
}
