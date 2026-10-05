import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import FeedbackForm from '../src/components/FeedbackForm';
import Navbar from '../src/components/Navbar';
import About from '../src/pages/About';
import Impact from '../src/pages/Impact';
import Placeholder from '../src/pages/Placeholder';
import Audit from '../src/pages/admin/Audit';
import AwarenessAdmin from '../src/pages/admin/AwarenessAdmin';
import Analytics from '../src/pages/admin/Analytics';
import Exports from '../src/pages/admin/Exports';
import FeedbackAdmin from '../src/pages/admin/FeedbackAdmin';
import ReportDetail from '../src/pages/admin/ReportDetail';
import AdminReports from '../src/pages/admin/Reports';

vi.mock('recharts', () => {
  const stub = () => null;
  return {
    ResponsiveContainer: stub, BarChart: stub, Bar: stub, LineChart: stub,
    Line: stub, PieChart: stub, Pie: stub, Cell: stub, XAxis: stub,
    YAxis: stub, CartesianGrid: stub, Tooltip: stub, Legend: stub,
  };
});

const reportRow = {
  id: '11111111-2222-3333-4444-555555555555',
  category: 'PHISHING', content_type: 'message', risk_level: 'HIGH',
  approximate_area: 'Demo Town', reported_at: '2026-09-01T10:00:00Z', status: 'PENDING',
};

beforeEach(() => {
  vi.spyOn(api, 'getImpactSummary').mockResolvedValue({ has_data: false });
  vi.spyOn(api, 'submitFeedback').mockResolvedValue({ id: 'f-1' });
  vi.spyOn(api, 'adminReports').mockResolvedValue([reportRow]);
  vi.spyOn(api, 'adminReport').mockResolvedValue({
    ...reportRow, sanitized_content: 'demo content', description: null,
    content_hash: 'abc', duplicate_count: 0, duplicate_ids: [], report_count: 1,
  });
  vi.spyOn(api, 'adminUpdateReportStatus').mockResolvedValue({ id: reportRow.id, status: 'REVIEWED' });
  vi.spyOn(api, 'adminAnalyticsSummary').mockResolvedValue({
    stats: { total_reports: 1, risk_distribution: { HIGH: 1 } },
    trends: [], categories: [], areas: [], content_types: { message: 1 },
    impact: { awareness_sessions_completed: 0, quizzes_completed: 0, avg_score_change: null },
  });
  vi.spyOn(api, 'adminAwarenessSummary').mockResolvedValue({
    has_data: false, total_sessions_started: 0, completed_before: 0, completed_after: 0,
    awareness_sessions_completed: 0, avg_before_score: null, avg_after_score: null,
    avg_score_change: null, quizzes_completed: 0, most_difficult_category: null,
    most_reviewed_topic: null,
  });
  vi.spyOn(api, 'adminFeedback').mockResolvedValue([]);
  vi.spyOn(api, 'adminFeedbackStats').mockResolvedValue({ total: 0, average_rating: null, by_topic: [], by_category: [] });
  vi.spyOn(api, 'adminAudit').mockResolvedValue([]);
});

describe('page render smoke (no crashes, honest states)', () => {
  test('navbar renders links and toggles mobile menu', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Navbar backendStatus="online" /></MemoryRouter>);
    expect(screen.getByRole('link', { name: /cybershield/i })).toBeInTheDocument();
    expect(screen.getByText('Service online')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /open menu/i }));
    expect(screen.getAllByRole('link', { name: 'Quiz' }).length).toBe(2);
  });

  test('about and placeholder render', () => {
    render(<MemoryRouter><About /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: /about cybershield community/i })).toBeInTheDocument();
  });

  test('impact empty state is honest', async () => {
    render(<MemoryRouter><Impact /></MemoryRouter>);
    expect(await screen.findByText('Not enough field data yet.')).toBeInTheDocument();
  });

  test('impact with data renders figures', async () => {
    api.getImpactSummary.mockResolvedValue({
      has_data: true, quizzes_completed: 4, awareness_sessions_completed: 2,
      avg_score_change: 1.5, avg_before_score: 3, avg_after_score: 4.5,
      most_difficult_category: 'Phishing', most_reviewed_topic: 'OTP scams',
    });
    render(<MemoryRouter><Impact /></MemoryRouter>);
    expect(await screen.findByText('Quizzes completed')).toBeInTheDocument();
    expect(screen.getByText(/quiz performance on this platform only/i)).toBeInTheDocument();
  });

  test('feedback form submits anonymously', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><FeedbackForm /></MemoryRouter>);
    await user.type(screen.getByLabelText(/topic/i), 'OTP session');
    await user.click(screen.getByRole('radio', { name: '5 out of 5' }));
    await user.click(screen.getByRole('button', { name: /submit anonymous feedback/i }));
    await waitFor(() => expect(api.submitFeedback).toHaveBeenCalled());
    expect(await screen.findByText(/thank you for your feedback/i)).toBeInTheDocument();
  });

  test('admin reports table renders rows and status', async () => {
    render(<MemoryRouter><AdminReports /></MemoryRouter>);
    const table = await screen.findByRole('table');
    expect(within(table).getByText('PHISHING')).toBeInTheDocument();
    expect(within(table).getByText('PENDING')).toBeInTheDocument();
    expect(within(table).getByRole('button', { name: 'Open' })).toBeInTheDocument();
  });

  test('report detail moderation flow works', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={[`/admin/reports/${reportRow.id}`]}>
        <Routes><Route path="/admin/reports/:id" element={<ReportDetail />} /></Routes>
      </MemoryRouter>,
    );
    expect(await screen.findByText(/community-submitted information/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Mark Reviewed' }));
    await user.click(screen.getByRole('button', { name: 'Confirm change' }));
    await waitFor(() => expect(api.adminUpdateReportStatus).toHaveBeenCalledWith(reportRow.id, 'REVIEWED'));
    expect(await screen.findByText(/recorded in the audit log/i)).toBeInTheDocument();
  });

  test('admin analytics renders without crashing', async () => {
    render(<MemoryRouter><Analytics /></MemoryRouter>);
    expect(await screen.findByText('Analytics')).toBeInTheDocument();
    expect(screen.getByText(/reports in scope/i)).toBeInTheDocument();
  });

  test('awareness admin shows honest empty state', async () => {
    render(<MemoryRouter><AwarenessAdmin /></MemoryRouter>);
    expect(await screen.findByText('Awareness impact')).toBeInTheDocument();
    expect(screen.getByText(/not enough data yet/i)).toBeInTheDocument();
  });

  test('feedback admin shows empty state', async () => {
    render(<MemoryRouter><FeedbackAdmin /></MemoryRouter>);
    expect(await screen.findByText('Field-study feedback')).toBeInTheDocument();
    expect(await screen.findByText('No feedback yet.')).toBeInTheDocument();
  });

  test('exports lists all three datasets', () => {
    render(<MemoryRouter><Exports /></MemoryRouter>);
    expect(screen.getByText('Data exports')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /export reports\.csv/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /export awareness\.csv/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /export feedback\.csv/i })).toBeInTheDocument();
  });

  test('audit log renders filters and empty state', async () => {
    render(<MemoryRouter><Audit /></MemoryRouter>);
    expect(await screen.findByText('Audit logs')).toBeInTheDocument();
    expect(screen.getByLabelText(/action/i)).toBeInTheDocument();
    expect(screen.getByText('No audit entries match.')).toBeInTheDocument();
  });

  test('placeholder 404 renders with home action', () => {
    render(<MemoryRouter><Placeholder /></MemoryRouter>);
    expect(screen.getByText('Page not found')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /back to home/i })).toBeInTheDocument();
  });
});
