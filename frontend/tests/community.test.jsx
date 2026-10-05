import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import Community from '../src/pages/Community';

vi.mock('recharts', () => {
  const stub = () => null;
  return {
    ResponsiveContainer: stub, BarChart: stub, Bar: stub, LineChart: stub,
    Line: stub, PieChart: stub, Pie: stub, Cell: stub, XAxis: stub,
    YAxis: stub, CartesianGrid: stub, Tooltip: stub, Legend: stub,
  };
});

const stats = {
  total_reports: 3, high_risk_reports: 1, most_reported_category: 'PHISHING',
  reports_this_week: 2, categories: { PHISHING: 3 },
  risk_distribution: { LOW: 1, MEDIUM: 1, HIGH: 1 },
};

beforeEach(() => {
  vi.spyOn(api, 'getCommunityStats').mockResolvedValue(stats);
  vi.spyOn(api, 'getCommunityTrends').mockResolvedValue([{ date: '2026-09-01', reports: 3 }]);
  vi.spyOn(api, 'getCommunityCategories').mockResolvedValue(
    [{ category: 'PHISHING', report_count: 3, percentage: 100 }]);
  vi.spyOn(api, 'getCommunityAreas').mockResolvedValue([{ area: 'Bhatkal', reports: 3 }]);
});

describe('community dashboard', () => {
  test('renders aggregated stats and area table', async () => {
    render(<MemoryRouter><Community /></MemoryRouter>);
    expect(await screen.findByText('Community dashboard')).toBeInTheDocument();
    expect(screen.getByText('Community reports')).toBeInTheDocument();
    expect(screen.getByText('Reports this week')).toBeInTheDocument();
    expect(screen.getByText('Bhatkal')).toBeInTheDocument();
    expect(screen.queryByText(/no community reports yet/i)).not.toBeInTheDocument();
  });

  test('empty state is explicit, not fabricated', async () => {
    api.getCommunityStats.mockResolvedValue({ ...stats, total_reports: 0 });
    api.getCommunityAreas.mockResolvedValue([]);
    render(<MemoryRouter><Community /></MemoryRouter>);
    expect(await screen.findByText(/no community reports yet/i)).toBeInTheDocument();
  });

  test('granularity switch refetches trends', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Community /></MemoryRouter>);
    await screen.findByText('Community dashboard');
    await user.click(screen.getByRole('button', { name: 'Weekly' }));
    await waitFor(() => expect(api.getCommunityTrends).toHaveBeenCalledWith('week'));
  });

  test('API failure shows an error state', async () => {
    api.getCommunityStats.mockRejectedValue(new Error('down'));
    render(<MemoryRouter><Community /></MemoryRouter>);
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
