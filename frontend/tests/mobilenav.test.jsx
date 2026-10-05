import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import BottomNav from '../src/components/BottomNav';
import Navbar from '../src/components/Navbar';
import QuizRunner from '../src/components/QuizRunner';
import Home from '../src/pages/Home';
import AdminReports from '../src/pages/admin/Reports';

beforeEach(() => {
  vi.spyOn(api, 'adminReports').mockResolvedValue([
    {
      id: '11111111-2222-3333-4444-555555555555',
      category: 'BANKING_SCAM', content_type: 'message', risk_level: 'HIGH',
      approximate_area: 'Bhatkal', reported_at: '2026-10-02T10:00:00Z', status: 'PENDING',
    },
  ]);
});

describe('mobile navigation', () => {
  test('bottom bar offers the four primary destinations', () => {
    render(<MemoryRouter><BottomNav /></MemoryRouter>);
    const nav = screen.getByRole('navigation', { name: /primary mobile/i });
    expect(nav).toBeInTheDocument();
    for (const [name, href] of [['Home', '/'], ['Check', '/analyze'], ['Community', '/community'], ['Learn', '/learn']]) {
      const link = screen.getByRole('link', { name });
      expect(link).toHaveAttribute('href', href);
    }
    expect(screen.getAllByRole('link').length).toBe(4);
  });

  test('bottom bar stays out of the admin console', () => {
    render(<MemoryRouter initialEntries={['/admin/reports']}><BottomNav /></MemoryRouter>);
    expect(screen.queryByRole('navigation', { name: /primary mobile/i })).not.toBeInTheDocument();
  });

  test('menu button opens a full-screen drawer with every section', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Navbar backendStatus="online" /></MemoryRouter>);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /open menu/i }));
    const dialog = await screen.findByRole('dialog');
    expect(dialog).toBeInTheDocument();
    for (const name of ['Home', 'Check Message', 'Check URL', 'Community', 'Learn', 'Quiz',
      'Report a Scam', 'Awareness Check', 'Community Impact', 'About']) {
      expect(within(dialog).getByRole('link', { name })).toBeInTheDocument();
    }
    await user.click(screen.getByRole('button', { name: /close menu/i }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  test('escape key closes the drawer (keyboard accessible)', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Navbar backendStatus="online" /></MemoryRouter>);
    await user.click(screen.getByRole('button', { name: /open menu/i }));
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});

describe('mobile-first content', () => {
  test('home shows compact topic rows linking to learn', () => {
    render(<MemoryRouter><Home /></MemoryRouter>);
    const rows = screen.getAllByRole('link').filter((l) => l.getAttribute('href') === '/learn');
    expect(rows.length).toBeGreaterThanOrEqual(6);
    const text = rows.map((l) => l.textContent).join(' ');
    for (const topic of ['Phishing', 'Banking scams', 'OTP scams', 'Job scams', 'Investment scams', 'Digital arrest']) {
      expect(text).toContain(topic);
    }
  });

  test('quiz uses compact counter and 48px options', () => {
    const questions = [
      { id: 1, category: 'Phishing', question: 'Q1?', options: ['Yes', 'No'], difficulty: 'easy' },
      { id: 2, category: 'Phishing', question: 'Q2?', options: ['Yes', 'No'], difficulty: 'easy' },
    ];
    render(<MemoryRouter><QuizRunner questions={questions} submitLabel="See my score" onSubmit={vi.fn()} /></MemoryRouter>);
    expect(screen.getByText('Question 1 / 2')).toBeInTheDocument();
    for (const opt of screen.getAllByRole('button', { name: /yes|no/i })) {
      expect(opt.className).toMatch(/min-h-\[48px\]/);
    }
  });

  test('admin reports render mobile cards with view action', async () => {
    render(<MemoryRouter><AdminReports /></MemoryRouter>);
    const viewButtons = await screen.findAllByRole('button', { name: 'View report' });
    expect(viewButtons.length).toBeGreaterThan(0);
    await waitFor(() => expect(api.adminReports).toHaveBeenCalled());
    expect(screen.getAllByText('BANKING_SCAM').length).toBeGreaterThan(0);
  });
});
