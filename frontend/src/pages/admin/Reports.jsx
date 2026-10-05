import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import LoadingState from '../../components/LoadingState';
import { Alert, Badge, Button, Card, EmptyState, Field, ReportCard, Select, Table, Td, TextInput, Th } from '../../components/ui';
import { adminReports } from '../../api';

const CATEGORIES = ['', 'PHISHING', 'BANKING_SCAM', 'JOB_SCAM', 'INVESTMENT_SCAM', 'DELIVERY_SCAM', 'OTP_SCAM', 'DIGITAL_ARREST', 'FAKE_SUPPORT', 'OTHER_SCAM', 'NORMAL'];
const RISKS = ['', 'LOW', 'MEDIUM', 'HIGH'];
const TYPES = ['', 'message', 'url'];
const STATUSES = ['', 'PENDING', 'REVIEWED', 'ARCHIVED'];

const statusTone = { PENDING: 'amber', REVIEWED: 'green', ARCHIVED: 'slate' };
const riskTone = { LOW: 'green', MEDIUM: 'amber', HIGH: 'red' };

function Filter({ label, htmlFor, children }) {
  return (
    <Field label={label} htmlFor={htmlFor}>
      {children}
    </Field>
  );
}

export default function AdminReports() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    category: '', risk_level: '', content_type: '', status: '', area: '', search: '',
  });

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
    adminReports(params)
      .then((d) => { if (mounted) setRows(d); })
      .catch(() => { if (mounted) setError('Report data temporarily unavailable.'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [filters]);

  const set = (k) => (v) => setFilters((f) => ({ ...f, [k]: v }));

  return (
    <div>
      <h1 className="text-xl font-bold tracking-tight text-ink">Reports</h1>
      <p className="mt-1 text-[13px] text-muted">Anonymized community submissions. Automated analysis is indicative, not confirmed fact.</p>

      <Card title="Filters" className="mt-4">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <Filter label="Category" htmlFor="flt-category">
            <Select id="flt-category" value={filters.category} onChange={(e) => set('category')(e.target.value)}>
              {options(CATEGORIES)}
            </Select>
          </Filter>
          <Filter label="Risk" htmlFor="flt-risk">
            <Select id="flt-risk" value={filters.risk_level} onChange={(e) => set('risk_level')(e.target.value)}>
              {options(RISKS)}
            </Select>
          </Filter>
          <Filter label="Type" htmlFor="flt-type">
            <Select id="flt-type" value={filters.content_type} onChange={(e) => set('content_type')(e.target.value)}>
              {options(TYPES)}
            </Select>
          </Filter>
          <Filter label="Status" htmlFor="flt-status">
            <Select id="flt-status" value={filters.status} onChange={(e) => set('status')(e.target.value)}>
              {options(STATUSES)}
            </Select>
          </Filter>
          <Filter label="Area" htmlFor="flt-area">
            <TextInput
              id="flt-area"
              value={filters.area}
              onChange={(e) => setFilters((f) => ({ ...f, area: e.target.value }))}
              placeholder="Locality…"
              maxLength={100}
            />
          </Filter>
          <Filter label="Search" htmlFor="flt-search">
            <TextInput
              id="flt-search"
              value={filters.search}
              onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
              placeholder="Category, area, ID…"
              maxLength={100}
            />
          </Filter>
        </div>
      </Card>

      {loading && <div className="mt-4"><LoadingState label="Loading reports…" /></div>}
      {error && <div className="mt-4"><Alert tone="error">{error}</Alert></div>}

      {!loading && !error && rows.length === 0 && (
        <div className="mt-4">
          <EmptyState title="No reports match these filters." text="Adjust or clear the filters to see more reports." />
        </div>
      )}

      {!loading && rows.length > 0 && (
        <>
          {/* Mobile: stacked report cards instead of a squeezed table. */}
          <div className="mt-4 space-y-3 md:hidden">
            {rows.map((r) => (
              <ReportCard
                key={r.id}
                title={r.category}
                risk={r.risk_level
                  ? <Badge tone={riskTone[r.risk_level] || 'slate'}>{r.risk_level} risk</Badge>
                  : null}
                rows={[
                  ['Area', r.approximate_area || '—'],
                  ['Reported', new Date(r.reported_at).toLocaleDateString()],
                  ['Status', r.status.charAt(0) + r.status.slice(1).toLowerCase()],
                ]}
                action={(
                  <Link to={`/admin/reports/${r.id}`}>
                    <Button variant="secondary" className="h-11 w-full">View report</Button>
                  </Link>
                )}
              />
            ))}
          </div>
          <div className="mt-4 hidden md:block">
          <Table minWidth={760}>
            <thead>
              <tr>
                <Th>Report ID</Th>
                <Th>Category</Th>
                <Th>Type</Th>
                <Th>Risk</Th>
                <Th>Area</Th>
                <Th>Submitted</Th>
                <Th>Status</Th>
                <Th><span className="sr-only">Action</span></Th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="hover:bg-surface-2/50">
                  <Td className="font-mono text-[13px]">{r.id.slice(0, 8)}…</Td>
                  <Td className="font-medium text-ink">{r.category}</Td>
                  <Td>{r.content_type}</Td>
                  <Td>
                    {r.risk_level
                      ? <Badge tone={riskTone[r.risk_level] || 'slate'}>{r.risk_level}</Badge>
                      : '—'}
                  </Td>
                  <Td>{r.approximate_area || '—'}</Td>
                  <Td>{new Date(r.reported_at).toLocaleDateString()}</Td>
                  <Td>
                    <Badge tone={statusTone[r.status] || 'slate'}>{r.status}</Badge>
                  </Td>
                  <Td>
                    <Link to={`/admin/reports/${r.id}`}>
                      <Button variant="secondary" className="h-9 px-3 text-[13px]">Open</Button>
                    </Link>
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
          </div>
        </>
      )}
    </div>
  );

  function options(list) {
    return list.map((o) => (
      <option key={o} value={o}>{o === '' ? 'All' : o}</option>
    ));
  }
}
