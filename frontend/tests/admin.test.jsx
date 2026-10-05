import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import AdminDashboard from '../src/pages/admin/Dashboard';
import AdminLogin from '../src/pages/admin/Login';
import AdminLayout from '../src/pages/admin/AdminLayout';

const profile = { email: 'admin@test.local', role: 'ADMIN' };
const overview = {
  total_reports: 5, pending_reports: 2, reviewed_reports: 2, archived_reports: 1,
  high_risk_reports: 1, awareness_sessions_completed: 3, quiz_attempts: 4, feedback_count: 2,
};

beforeEach(() => {
  vi.spyOn(api, 'adminLogin').mockResolvedValue({
    access_token: 'tok', token_type: 'bearer', role: 'ADMIN', email: profile.email,
  });
  vi.spyOn(api, 'adminMe').mockResolvedValue(profile);
  vi.spyOn(api, 'adminOverview').mockResolvedValue(overview);
});

describe('admin login', () => {
  function setup() {
    render(
      <MemoryRouter initialEntries={['/admin/login']}>
        <Routes><Route path="/admin/login" element={<AdminLogin />} /></Routes>
      </MemoryRouter>,
    );
  }

  test('renders the login form', () => {
    setup();
    expect(screen.getByRole('heading', { name: /admin login/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  test('empty credentials are rejected client-side', async () => {
    const user = userEvent.setup();
    setup();
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    expect(await screen.findByText(/enter your admin email/i)).toBeInTheDocument();
    expect(api.adminLogin).not.toHaveBeenCalled();
  });

  test('successful login stores the session token', async () => {
    const user = userEvent.setup();
    const setToken = vi.spyOn(api, 'setAdminToken');
    setup();
    await user.type(screen.getByLabelText(/email/i), 'admin@test.local');
    await user.type(screen.getByLabelText(/password/i), 'Secret123!');
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    await waitFor(() => expect(api.adminLogin).toHaveBeenCalledWith('admin@test.local', 'Secret123!'));
    expect(setToken).toHaveBeenCalledWith('tok', { email: profile.email, role: 'ADMIN' });
  });

  test('server error message is displayed, not internals', async () => {
    const user = userEvent.setup();
    api.adminLogin.mockRejectedValue({
      response: { status: 401, data: { error: 'unauthorized', message: 'Invalid credentials.' } },
    });
    setup();
    await user.type(screen.getByLabelText(/email/i), 'a@b.cc');
    await user.type(screen.getByLabelText(/password/i), 'wrong');
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    expect(await screen.findByText('Invalid credentials.')).toBeInTheDocument();
  });
});

describe('protected admin routes', () => {
  function setupShell() {
    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );
  }

  test('no token redirects to the login page', async () => {
    vi.spyOn(api, 'getAdminToken').mockReturnValue(null);
    setupShell();
    expect(await screen.findByRole('heading', { name: /admin login/i })).toBeInTheDocument();
    expect(api.adminMe).not.toHaveBeenCalled();
  });

  test('invalid token is cleared and redirects to login', async () => {
    vi.spyOn(api, 'getAdminToken').mockReturnValue('stale');
    api.adminMe.mockRejectedValue({ response: { status: 401, data: {} } });
    const clear = vi.spyOn(api, 'clearAdminToken');
    setupShell();
    expect(await screen.findByRole('heading', { name: /admin login/i })).toBeInTheDocument();
    expect(clear).toHaveBeenCalled();
  });

  test('valid session renders the console, never the login form', async () => {
    vi.spyOn(api, 'getAdminToken').mockReturnValue('tok');
    setupShell();
    expect(await screen.findByText('Admin console')).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /admin login/i })).not.toBeInTheDocument();
  });
});

describe('admin dashboard', () => {
  test('renders real overview values and empty states honestly', async () => {
    render(<MemoryRouter><AdminDashboard /></MemoryRouter>);
    expect(await screen.findByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Pending review')).toBeInTheDocument();
    expect(screen.getByText('High-risk')).toBeInTheDocument();
    expect(screen.getByText('Moderation queue')).toBeInTheDocument();
  });

  test('empty database shows the not-enough-data notice', async () => {
    api.adminOverview.mockResolvedValue({ ...overview, total_reports: 0, quiz_attempts: 0 });
    render(<MemoryRouter><AdminDashboard /></MemoryRouter>);
    expect(await screen.findByText(/not enough data yet/i)).toBeInTheDocument();
  });

  test('API failure shows an error state', async () => {
    api.adminOverview.mockRejectedValue(new Error('down'));
    render(<MemoryRouter><AdminDashboard /></MemoryRouter>);
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
