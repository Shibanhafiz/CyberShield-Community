import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import LoadingState from '../components/LoadingState';
import { Alert, Card, Container, EmptyState, PageHeader, Stat, Table, Td, Th } from '../components/ui';
import {
  getCommunityAreas,
  getCommunityCategories,
  getCommunityStats,
  getCommunityTrends,
} from '../api';

const RISK_COLORS = { LOW: '#15803d', MEDIUM: '#d97706', HIGH: '#dc2626' };
const AXIS = '#64748b';
const GRID = '#e2e8f0';

const tooltipStyle = {
  backgroundColor: '#ffffff',
  border: '1px solid #e2e8f0',
  borderRadius: '8px',
  fontSize: '12px',
  color: '#0f172a',
};

export default function Community() {
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [areas, setAreas] = useState([]);
  const [granularity, setGranularity] = useState('day');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    Promise.all([
      getCommunityStats(),
      getCommunityTrends(granularity),
      getCommunityCategories(),
      getCommunityAreas(),
    ])
      .then(([s, t, c, a]) => {
        if (mounted) {
          setStats(s);
          setTrends(t);
          setCategories(c);
          setAreas(a);
        }
      })
      .catch(() => {
        if (mounted) setError('Community statistics are temporarily unavailable. Please try again later.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [granularity]);

  if (loading) {
    return (
      <Container>
        <LoadingState label="Loading community statistics…" />
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

  const isEmpty = stats.total_reports === 0;
  const riskData = Object.entries(stats.risk_distribution).map(([name, value]) => ({ name, value }));

  return (
    <Container>
      <PageHeader
        eyebrow="Community"
        title="Community dashboard"
        description="Aggregated, anonymized scam reports from the community. Reports are community-submitted and may require review — figures here are observations, not verified findings."
      />

      {isEmpty ? (
        <div className="mt-6">
          <EmptyState
            title="No community reports yet."
            text="Reports submitted through CyberShield will appear here after they are recorded."
          />
        </div>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Stat label="Community reports" value={stats.total_reports} />
            <Stat label="Reports this week" value={stats.reports_this_week} />
            <Stat label="Most reported category" value={stats.most_reported_category || '—'} />
            <Stat label="High-risk reports" value={stats.high_risk_reports} />
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <Card title="Reports by category">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={categories} layout="vertical" margin={{ left: 8, right: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
                  <XAxis type="number" stroke={AXIS} fontSize={11} allowDecimals={false} />
                  <YAxis type="category" dataKey="category" stroke={AXIS} fontSize={11} width={120} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="report_count" name="Reports" fill="#2563eb" radius={[0, 4, 4, 0]} isAnimationActive={false} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Reports by risk level">
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3} isAnimationActive={false}>
                    {riskData.map((r) => (
                      <Cell key={r.name} fill={RISK_COLORS[r.name] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>

          <div className="mt-4">
            <Card
              title="Reports over time"
              action={(
                <div className="flex gap-1.5" role="group" aria-label="Time granularity">
                  {['day', 'week', 'month'].map((g) => (
                    <button
                      key={g}
                      onClick={() => setGranularity(g)}
                      aria-pressed={granularity === g}
                      className={`h-8 rounded-lg px-3 text-[13px] font-semibold ${
                        granularity === g ? 'bg-brand-tint text-brand-dark' : 'text-ink-2 hover:bg-surface-2'
                      }`}
                    >
                      {g === 'day' ? 'Daily' : g === 'week' ? 'Weekly' : 'Monthly'}
                    </button>
                  ))}
                </div>
              )}
            >
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={trends} margin={{ left: -12, right: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
                  <XAxis dataKey="date" stroke={AXIS} fontSize={10} tickMargin={8} minTickGap={32} />
                  <YAxis stroke={AXIS} fontSize={11} allowDecimals={false} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Line type="monotone" dataKey="reports" name="Reports" stroke="#2563eb" strokeWidth={2} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </div>

          <div className="mt-4">
            <Card title="Reports by approximate area">
              <p className="mb-3 text-[13px] text-muted">
                Coarse localities only — no addresses, coordinates or identities.
              </p>
              <Table minWidth={0}>
                <thead>
                  <tr>
                    <Th>Area</Th>
                    <Th>Reports</Th>
                  </tr>
                </thead>
                <tbody>
                  {areas.map((a) => (
                    <tr key={a.area}>
                      <Td>{a.area}</Td>
                      <Td className="font-semibold text-ink">{a.reports}</Td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card>
          </div>
        </>
      )}

      <Alert tone="info" className="mt-6">
        Do not submit passwords, OTPs, card details or other sensitive information.
        Community reports are anonymized observations, not verified security intelligence.
      </Alert>
    </Container>
  );
}
