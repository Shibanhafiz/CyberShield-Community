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
import LoadingState from '../../components/LoadingState';
import StatCard from '../../components/StatCard';
import { Alert, Card, EmptyState, Table, Td, Th } from '../../components/ui';
import { adminAnalyticsSummary } from '../../api';

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

function Empty({ label }) {
  return <EmptyState title="Not enough data yet." text={`No data for ${label} in the selected scope.`} />;
}

export default function AdminAnalytics() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    adminAnalyticsSummary()
      .then((d) => { if (mounted) setData(d); })
      .catch(() => { if (mounted) setError('Analytics temporarily unavailable.'); });
    return () => { mounted = false; };
  }, []);

  if (error) {
    return <Alert tone="error">{error}</Alert>;
  }

  if (!data) return <LoadingState label="Loading analytics…" />;

  const riskData = Object.entries(data.stats.risk_distribution).map(([name, value]) => ({ name, value }));
  const typeData = Object.entries(data.content_types).map(([name, value]) => ({ name, value }));
  const hasReports = data.stats.total_reports > 0;

  return (
    <div>
      <h1 className="text-xl font-bold tracking-tight text-ink">Analytics</h1>
      <p className="mt-1 text-[13px] text-muted">Aggregated project data — {data.stats.total_reports} reports in scope.</p>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card title="Reports over time (daily)">
          {hasReports ? (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={data.trends} margin={{ left: -12, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
                <XAxis dataKey="date" stroke={AXIS} fontSize={10} minTickGap={40} />
                <YAxis stroke={AXIS} fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey="reports" stroke="#2563eb" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : <Empty label="trends" />}
        </Card>

        <Card title="Reports by category">
          {data.categories.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={data.categories} layout="vertical" margin={{ left: 8, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
                <XAxis type="number" stroke={AXIS} fontSize={11} allowDecimals={false} />
                <YAxis type="category" dataKey="category" stroke={AXIS} fontSize={11} width={120} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="report_count" name="Reports" fill="#2563eb" radius={[0, 4, 4, 0]} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          ) : <Empty label="categories" />}
        </Card>

        <Card title="Reports by risk level">
          {hasReports ? (
            <ResponsiveContainer width="100%" height={240}>
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
          ) : <Empty label="risk levels" />}
        </Card>

        <Card title="Reports by content type">
          {typeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={typeData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3} isAnimationActive={false}>
                  {typeData.map((t, i) => (
                    <Cell key={t.name} fill={i === 0 ? '#2563eb' : '#64748b'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : <Empty label="content types" />}
        </Card>
      </div>

      <div className="mt-4">
        <Card title="Reports by approximate area">
          {data.areas.length > 0 ? (
            <Table minWidth={0}>
              <thead>
                <tr>
                  <Th>Area</Th>
                  <Th>Reports</Th>
                </tr>
              </thead>
              <tbody>
                {data.areas.map((a) => (
                  <tr key={a.area}>
                    <Td>{a.area}</Td>
                    <Td className="font-semibold text-ink">{a.reports}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : <Empty label="areas" />}
        </Card>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatCard label="Awareness sessions" value={data.impact.awareness_sessions_completed} />
        <StatCard label="Quiz attempts" value={data.impact.quizzes_completed} />
        <StatCard
          label="Avg score change"
          value={data.impact.avg_score_change == null ? '—' : `${data.impact.avg_score_change >= 0 ? '+' : ''}${data.impact.avg_score_change}`}
        />
      </div>
    </div>
  );
}
