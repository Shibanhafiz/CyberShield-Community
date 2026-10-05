import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import Learn from '../src/pages/Learn';
import Scenario from '../src/pages/Scenario';

const topics = [
  { slug: 'phishing', title: 'Phishing Messages & Fake Links', category: 'Phishing', description: 'Spot fake links.' },
];
const scenarios = [
  { scenario_id: 'scn-01', category: 'Phishing', title: 'Blocked account?', difficulty: 'easy' },
];
const scenarioDetail = {
  scenario_id: 'scn-01', category: 'Phishing', title: 'Blocked account?', difficulty: 'easy',
  message: 'Your account will be blocked. Send OTP now.',
  warning_signals: ['Urgency', 'OTP request'],
  choices: ['Ignore and verify via official app', 'Send the OTP', 'Click and log in', 'Forward to friends'],
  explanation: 'Banks never ask for OTPs.',
  recommended_action: 'Ignore and verify via official app',
};

beforeEach(() => {
  vi.spyOn(api, 'getTopics').mockResolvedValue(topics);
  vi.spyOn(api, 'getScenarios').mockResolvedValue(scenarios);
  vi.spyOn(api, 'getTopic').mockResolvedValue({
    ...topics[0], what_it_is: 'Fake messages.', warning_signs: ['Urgency'],
    example: 'Example.', attacker_goal: 'Theft.', should_do: ['Verify'],
    never_do: ['Share OTP'],
  });
  vi.spyOn(api, 'getScenario').mockResolvedValue(scenarioDetail);
  vi.spyOn(api, 'answerScenario').mockResolvedValue({
    safe_choice: true, correct_action: scenarioDetail.recommended_action,
    warning_signals: scenarioDetail.warning_signals, explanation: scenarioDetail.explanation,
  });
});

describe('learning page', () => {
  test('lists topics and scenarios', async () => {
    render(<MemoryRouter><Learn /></MemoryRouter>);
    expect(await screen.findByText('Phishing Messages & Fake Links')).toBeInTheDocument();
    expect(screen.getByText('Blocked account?')).toBeInTheDocument();
  });

  test('expanding a topic loads its detail', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Learn /></MemoryRouter>);
    await user.click(await screen.findByText('Phishing Messages & Fake Links'));
    await waitFor(() => expect(api.getTopic).toHaveBeenCalledWith('phishing'));
    expect(await screen.findByText('Fake messages.')).toBeInTheDocument();
  });

  test('topic load failure shows an error, not a crash', async () => {
    const user = userEvent.setup();
    api.getTopic.mockRejectedValue(new Error('down'));
    render(<MemoryRouter><Learn /></MemoryRouter>);
    await user.click(await screen.findByText('Phishing Messages & Fake Links'));
    expect(await screen.findByText(/could not load this topic/i)).toBeInTheDocument();
  });
});

describe('scenario flow', () => {
  function setup() {
    render(
      <MemoryRouter initialEntries={['/learn/scenario/scn-01']}>
        <Routes><Route path="/learn/scenario/:id" element={<Scenario />} /></Routes>
      </MemoryRouter>,
    );
  }

  test('scenario renders choices and accepts an answer', async () => {
    const user = userEvent.setup();
    setup();
    expect(await screen.findByText('Your account will be blocked. Send OTP now.')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /ignore and verify/i }));
    await waitFor(() => expect(api.answerScenario).toHaveBeenCalledWith('scn-01', 0));
    expect(await screen.findByText('Banks never ask for OTPs.')).toBeInTheDocument();
  });

  test('scenario load failure shows an error state', async () => {
    api.getScenario.mockRejectedValue(new Error('down'));
    setup();
    expect(await screen.findByText(/could not load this scenario/i)).toBeInTheDocument();
  });
});
