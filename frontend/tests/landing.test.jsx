import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, test } from 'vitest';
import Home from '../src/pages/Home';

describe('landing page', () => {
  test('renders headline and primary actions', () => {
    render(<MemoryRouter><Home /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: /check before you trust/i })).toBeInTheDocument();
    const messageLinks = screen.getAllByRole('link', { name: /check a message/i });
    expect(messageLinks.length).toBeGreaterThan(0);
    expect(messageLinks[0]).toHaveAttribute('href', '/analyze');
    const urlLinks = screen.getAllByRole('link', { name: /check a url/i });
    expect(urlLinks.length).toBeGreaterThan(0);
    expect(urlLinks[0]).toHaveAttribute('href', '/analyze/url');
  });

  test('states honesty limits instead of marketing claims', () => {
    render(<MemoryRouter><Home /></MemoryRouter>);
    expect(screen.getByText(/indicative only/i)).toBeInTheDocument();
    expect(screen.queryByText(/ai-powered/i)).not.toBeInTheDocument();
  });

  test('explains the workflow in practical steps', () => {
    render(<MemoryRouter><Home /></MemoryRouter>);
    for (const step of ['Paste', 'Analyze', 'Understand', 'Act safely']) {
      expect(screen.getByText(step)).toBeInTheDocument();
    }
  });
});
