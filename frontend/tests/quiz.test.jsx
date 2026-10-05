import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import Quiz from '../src/pages/Quiz';

const questions = [
  { id: 1, category: 'Phishing', question: 'What is phishing?', options: ['A scam', 'A fish'], difficulty: 'easy' },
  { id: 2, category: 'OTP & Banking', question: 'Share your OTP?', options: ['Never', 'Always'], difficulty: 'easy' },
];
const result = {
  attempt_id: 'a-1', score: 2, total: 2,
  category_scores: { Phishing: { correct: 1, total: 1 }, 'OTP & Banking': { correct: 1, total: 1 } },
  recommendations: [],
  results: [
    { question_id: 1, category: 'Phishing', correct: true, explanation: 'Good.' },
    { question_id: 2, category: 'OTP & Banking', correct: true, explanation: 'Good.' },
  ],
};

beforeEach(() => {
  vi.spyOn(api, 'getQuizQuestions').mockResolvedValue(questions);
  vi.spyOn(api, 'submitQuizAttempt').mockResolvedValue(result);
});

describe('quiz page', () => {
  test('loads and renders questions with progress', async () => {
    render(<MemoryRouter><Quiz /></MemoryRouter>);
    expect(await screen.findByText('Awareness quiz')).toBeInTheDocument();
    expect(screen.getByText('What is phishing?')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('answering all questions and submitting shows the score', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Quiz /></MemoryRouter>);
    await screen.findByText('What is phishing?');
    await user.click(screen.getByRole('button', { name: /a scam/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));
    await user.click(screen.getByRole('button', { name: /never/i }));
    await user.click(screen.getByRole('button', { name: /see my score/i }));
    await waitFor(() => expect(api.submitQuizAttempt).toHaveBeenCalled());
    expect(await screen.findByText('Your score')).toBeInTheDocument();
    expect(screen.getByText(/category strengths/i)).toBeInTheDocument();
    expect(screen.getByText(/review your answers/i)).toBeInTheDocument();
  });

  test('load failure shows an error state', async () => {
    api.getQuizQuestions.mockRejectedValue(new Error('down'));
    render(<MemoryRouter><Quiz /></MemoryRouter>);
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
