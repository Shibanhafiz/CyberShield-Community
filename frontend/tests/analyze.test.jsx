import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import Analyze from '../src/pages/Analyze';

const messageResult = {
  risk_level: 'HIGH',
  risk_score: 82,
  category: 'OTP_SCAM',
  category_label: 'OTP Scam',
  model_confidence: 0.71,
  model_version: 'baseline-v1',
  ml_available: true,
  indicators: [{ code: 'OTP_REQUEST', severity: 'high', title: 'OTP request', description: 'Asks for an OTP.' }],
  urls: [],
  explanation: 'Potentially suspicious.',
  recommendation: 'Do not share OTPs.',
  disclaimer: 'Automated analysis, not proof.',
};

const urlResult = {
  url: 'http://example.com/login',
  risk_level: 'MEDIUM',
  risk_score: 45,
  signals: [{ code: 'SUSPICIOUS_PATH', severity: 'medium', title: 'Login path', description: 'Login-like path.' }],
  technical_details: {
    scheme: 'http', hostname: 'example.com', punycode: 'example.com', domain: 'example.com',
    subdomains: [], tld: 'com', uses_https: false, uses_ip_address: false,
    is_private_ip: false, port: null, url_length: 26, hostname_length: 11,
  },
  reputation: { available: false, source: null, verdict: null, reason: 'No provider configured.' },
  explanation: 'Static signals only.',
  recommendation: 'Verify the sender.',
  disclaimer: 'Static analysis cannot prove maliciousness.',
};

function serverError(message, status = 400) {
  return { response: { status, data: { error: 'invalid_request', message } } };
}

beforeEach(() => {
  vi.spyOn(api, 'analyzeMessage').mockResolvedValue(messageResult);
  vi.spyOn(api, 'analyzeUrl').mockResolvedValue(urlResult);
});

describe('analyzer page', () => {
  test('renders tabs and input', () => {
    render(<MemoryRouter><Analyze /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: /check a suspicious message/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Message' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'URL' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Analyze message' })).toBeInTheDocument();
    expect(screen.getByText(/enter passwords, otps/i)).toBeInTheDocument();
  });

  test('empty message shows a client-side hint without calling the API', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Analyze /></MemoryRouter>);
    await user.click(screen.getByRole('button', { name: 'Analyze message' }));
    expect(await screen.findByText(/paste a message first/i)).toBeInTheDocument();
    expect(api.analyzeMessage).not.toHaveBeenCalled();
  });

  test('successful message analysis shows risk and category', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Analyze /></MemoryRouter>);
    await user.type(screen.getByRole('textbox'), 'Your OTP is needed urgently.');
    await user.click(screen.getByRole('button', { name: 'Analyze message' }));
    await waitFor(() => expect(api.analyzeMessage).toHaveBeenCalled());
    expect(await screen.findByText('Analysis result')).toBeInTheDocument();
    expect(screen.getByText('OTP Scam')).toBeInTheDocument();
    expect(screen.getByText(/why this was flagged/i)).toBeInTheDocument();
    expect(screen.getByText(/recommended action/i)).toBeInTheDocument();
  });

  test('server error message is displayed (Phase 7 shape)', async () => {
    const user = userEvent.setup();
    api.analyzeMessage.mockRejectedValue(serverError('The submitted message is not valid.'));
    render(<MemoryRouter><Analyze /></MemoryRouter>);
    await user.type(screen.getByRole('textbox'), 'x');
    await user.click(screen.getByRole('button', { name: 'Analyze message' }));
    expect(await screen.findByText('The submitted message is not valid.')).toBeInTheDocument();
  });

  test('URL tab analyzes and renders technical details', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter initialEntries={['/analyze/url']}><Analyze initialTab="url" /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: /check a suspicious link/i })).toBeInTheDocument();
    await user.type(screen.getByRole('textbox'), 'http://example.com/login');
    await user.click(screen.getByRole('button', { name: 'Analyze URL' }));
    await waitFor(() => expect(api.analyzeUrl).toHaveBeenCalledWith('http://example.com/login'));
    expect(await screen.findByText('URL analysis')).toBeInTheDocument();
    expect(screen.getByText('Technical details')).toBeInTheDocument();
    expect(screen.getByText(/threat-intelligence check: unavailable/i)).toBeInTheDocument();
  });

  test('offline backend shows connectivity message', async () => {
    const user = userEvent.setup();
    api.analyzeMessage.mockRejectedValue({});
    render(<MemoryRouter><Analyze /></MemoryRouter>);
    await user.type(screen.getByRole('textbox'), 'hello');
    await user.click(screen.getByRole('button', { name: 'Analyze message' }));
    expect(await screen.findByText(/cannot reach the backend/i)).toBeInTheDocument();
  });
});
