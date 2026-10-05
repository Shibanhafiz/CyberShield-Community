import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import Report from '../src/pages/Report';

beforeEach(() => {
  vi.spyOn(api, 'submitReport').mockResolvedValue({
    success: true, report_id: 'r-1', duplicate: false, message: 'ok',
  });
});

describe('report flow', () => {
  function setup() {
    render(<MemoryRouter><Report /></MemoryRouter>);
  }

  test('renders form with privacy warning', () => {
    setup();
    expect(screen.getByRole('heading', { name: /report a scam/i })).toBeInTheDocument();
    expect(screen.getByText(/do not include passwords, otps/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/suspicious content/i)).toBeInTheDocument();
  });

  test('empty content is rejected client-side', async () => {
    const user = userEvent.setup();
    setup();
    await user.click(screen.getByRole('button', { name: /submit anonymous report/i }));
    expect(await screen.findByText(/paste the suspicious content/i)).toBeInTheDocument();
    expect(api.submitReport).not.toHaveBeenCalled();
  });

  test('successful submission shows thank-you state', async () => {
    const user = userEvent.setup();
    setup();
    await user.type(screen.getByLabelText(/suspicious content/i), 'Your account will be blocked.');
    await user.click(screen.getByRole('button', { name: /submit anonymous report/i }));
    await waitFor(() => expect(api.submitReport).toHaveBeenCalled());
    expect(await screen.findByText(/thank you for helping the community/i)).toBeInTheDocument();
  });

  test('server error message is surfaced', async () => {
    const user = userEvent.setup();
    api.submitReport.mockRejectedValue({
      response: { status: 429, data: { error: 'rate_limited', message: 'Too many reports.' } },
    });
    setup();
    await user.type(screen.getByLabelText(/suspicious content/i), 'spam spam');
    await user.click(screen.getByRole('button', { name: /submit anonymous report/i }));
    expect(await screen.findByText('Too many reports.')).toBeInTheDocument();
  });
});
