import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import Awareness from '../src/pages/Awareness';

const questions = [
  { id: 11, category: 'Phishing', question: 'Q1?', options: ['Yes', 'No'], difficulty: 'easy' },
];

beforeEach(() => {
  vi.spyOn(api, 'getQuizQuestions').mockResolvedValue(questions);
  vi.spyOn(api, 'getAwarenessSession').mockResolvedValue(null);
  vi.spyOn(api, 'submitBefore').mockResolvedValue({
    score: 1, total: 1, session: { session_id: 's', before_score: 1, before_total: 1 },
  });
  vi.spyOn(api, 'submitAfter').mockResolvedValue({
    score: 1, total: 1,
    session: { session_id: 's', before_score: 0, before_total: 1, after_score: 1, after_total: 1, score_difference: 1 },
  });
});

describe('awareness flow', () => {
  test('before assessment submits and moves to the learn stage', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Awareness /></MemoryRouter>);
    expect(await screen.findByText(/before \/ after assessment/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /yes/i }));
    await user.click(screen.getByRole('button', { name: /save & continue to learning/i }));
    await waitFor(() => expect(api.submitBefore).toHaveBeenCalled());
    expect(await screen.findByText(/before score saved/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start after assessment/i })).toBeInTheDocument();
  });

  test('load failure shows an error state', async () => {
    api.getQuizQuestions.mockRejectedValue(new Error('down'));
    render(<MemoryRouter><Awareness /></MemoryRouter>);
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
