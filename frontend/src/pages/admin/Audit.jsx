import { useEffect, useState } from 'react';
import LoadingState from '../../components/LoadingState';
import { Alert, Badge, Card, EmptyState, Field, Select, Table, Td, TextInput, Th } from '../../components/ui';
import { adminAudit } from '../../api';

const ACTIONS = ['', 'LOGIN_SUCCESS', 'LOGIN_FAILED', 'USER_CREATED', 'REPORT_REVIEWED', 'REPORT_ARCHIVED', 'REPORT_STATUS_CHANGED', 'DATA_EXPORT'];

export default function Audit() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [action, setAction] = useState('');
  const [resourceType, setResourceType] = useState('');

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    const params = {};
    if (action) params.action = action;
    if (resourceType) params.resource_type = resourceType;
    adminAudit(params)
      .then((d) => { if (mounted) setRows(d); })
      .catch(() => { if (mounted) setError('Audit data temporarily unavailable.'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [action, resourceType]);

  return (
    <div>
      <h1 className="text-xl font-bold tracking-tight text-ink">Audit logs</h1>
      <p className="mt-1 text-[13px] text-muted">Append-only record of admin actions. No secrets are stored here.</p>

      <Card title="Filters" className="mt-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Action" htmlFor="audit-action">
            <Select id="audit-action" value={action} onChange={(e) => setAction(e.target.value)}>
              {ACTIONS.map((a) => (
                <option key={a} value={a}>{a === '' ? 'All' : a}</option>
              ))}
            </Select>
          </Field>
          <Field label="Resource type" htmlFor="audit-resource">
            <TextInput
              id="audit-resource"
              value={resourceType}
              onChange={(e) => setResourceType(e.target.value)}
              placeholder="e.g. scam_report"
              maxLength={64}
            />
          </Field>
        </div>
      </Card>

      {loading && <div className="mt-4"><LoadingState label="Loading audit logs…" /></div>}
      {error && <div className="mt-4"><Alert tone="error">{error}</Alert></div>}

      {!loading && !error && rows.length === 0 && (
        <div className="mt-4">
          <EmptyState title="No audit entries match." text="Adjust the filters to see more entries." />
        </div>
      )}

      {!loading && rows.length > 0 && (
        <div className="mt-4">
          <Table minWidth={720}>
            <thead>
              <tr>
                <Th>Date</Th>
                <Th>Admin / Reviewer</Th>
                <Th>Action</Th>
                <Th>Resource</Th>
                <Th>Result</Th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="hover:bg-surface-2/50">
                  <Td>{new Date(r.created_at).toLocaleString()}</Td>
                  <Td>{r.admin_email || '—'}</Td>
                  <Td className="font-semibold text-ink">{r.action}</Td>
                  <Td className="font-mono text-[13px]">
                    {r.resource_type || '—'}{r.resource_id ? ` · ${String(r.resource_id).slice(0, 8)}…` : ''}
                  </Td>
                  <Td>
                    <Badge tone={r.result === 'success' ? 'green' : r.result === 'failed' ? 'red' : 'slate'}>
                      {r.result}
                    </Badge>
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </div>
  );
}
