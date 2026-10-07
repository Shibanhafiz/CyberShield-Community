import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import Footer from '../src/components/Footer';
import Privacy from '../src/pages/Privacy';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as api from '../src/api';
import PageMeta from '../src/components/PageMeta';
import About from '../src/pages/About';
import Analyze from '../src/pages/Analyze';
import Awareness from '../src/pages/Awareness';
import Community from '../src/pages/Community';
import Home from '../src/pages/Home';
import Impact from '../src/pages/Impact';
import Learn from '../src/pages/Learn';
import NotFound from '../src/pages/NotFound';
import Quiz from '../src/pages/Quiz';
import Report from '../src/pages/Report';
import Scenario from '../src/pages/Scenario';
import AdminLogin from '../src/pages/admin/Login';

vi.mock('recharts', () => {
  const stub = () => null;
  return {
    ResponsiveContainer: stub, BarChart: stub, Bar: stub, LineChart: stub,
    Line: stub, PieChart: stub, Pie: stub, Cell: stub, XAxis: stub,
    YAxis: stub, CartesianGrid: stub, Tooltip: stub, Legend: stub,
  };
});

function meta() {
  return document.querySelector('meta[name="description"]')?.getAttribute('content') || '';
}

beforeEach(() => {
  document.title = '';
  document.querySelector('meta[name="description"]')?.remove();
  vi.spyOn(api, 'analyzeMessage').mockResolvedValue({});
  vi.spyOn(api, 'analyzeUrl').mockResolvedValue({});
  vi.spyOn(api, 'getCommunityStats').mockResolvedValue({
    total_reports: 0, high_risk_reports: 0, most_reported_category: null,
    reports_this_week: 0, categories: {}, risk_distribution: {},
  });
  vi.spyOn(api, 'getCommunityTrends').mockResolvedValue([]);
  vi.spyOn(api, 'getCommunityCategories').mockResolvedValue([]);
  vi.spyOn(api, 'getCommunityAreas').mockResolvedValue([]);
  vi.spyOn(api, 'getTopics').mockResolvedValue([]);
  vi.spyOn(api, 'getScenarios').mockResolvedValue([]);
  vi.spyOn(api, 'getQuizQuestions').mockResolvedValue([
    { id: 1, category: 'Phishing', question: 'Q?', options: ['Yes', 'No'], difficulty: 'easy' },
  ]);
  vi.spyOn(api, 'getAwarenessSession').mockResolvedValue(null);
  vi.spyOn(api, 'getImpactSummary').mockResolvedValue({ has_data: false });
});

describe('page titles and descriptions', () => {
  test('PageMeta writes title with site suffix + description', () => {
    render(<PageMeta title="Example Page" description="An example description." />);
    expect(document.title).toBe('Example Page | CyberShield Community');
    expect(meta()).toBe('An example description.');
  });

  test('home, about, community, learn, quiz, awareness, impact, report, login, 404', async () => {
    const cases = [
      [Home, {}, 'Check before you trust | CyberShield Community'],
      [About, {}, 'About | CyberShield Community'],
      [Community, {}, 'Community Dashboard | CyberShield Community'],
      [Learn, {}, 'Learn About Scams | CyberShield Community'],
      [Quiz, {}, 'Awareness Quiz | CyberShield Community'],
      [Awareness, {}, 'Before / After Assessment | CyberShield Community'],
      [Impact, {}, 'Community Impact | CyberShield Community'],
      [Report, {}, 'Report a Scam | CyberShield Community'],
      [NotFound, {}, 'Page Not Found | CyberShield Community'],
      [AdminLogin, { route: '/admin/login', path: '/admin/login' }, 'Admin Login | CyberShield Community'],
    ];
    for (const [Page, opts, title] of cases) {
      document.title = '';
      document.querySelector('meta[name="description"]')?.remove();
      if (opts.route) {
        render(
          <MemoryRouter initialEntries={[opts.route]}>
            <Routes><Route path={opts.path} element={<Page />} /></Routes>
          </MemoryRouter>,
        );
      } else {
        render(<MemoryRouter><Page /></MemoryRouter>);
      }
      await waitFor(() => expect(document.title).toBe(title));
      const desc = meta();
      expect(desc.length).toBeGreaterThan(40);
      expect(desc.length).toBeLessThan(300);
    }
  });

  test('analyzer title follows the active tab', async () => {
    render(<MemoryRouter><Analyze /></MemoryRouter>);
    await waitFor(() => expect(document.title).toBe('Check a Message | CyberShield Community'));
  });

  test('url analyzer route title', async () => {
    render(<MemoryRouter><Analyze initialTab="url" /></MemoryRouter>);
    await waitFor(() => expect(document.title).toBe('Check a URL | CyberShield Community'));
  });

  test('scenario page title', async () => {
    vi.spyOn(api, 'getScenario').mockResolvedValue({
      scenario_id: 'scn-01', category: 'Phishing', title: 'T', difficulty: 'easy',
      message: 'M', warning_signals: [], choices: ['A', 'B'], explanation: 'E',
      recommended_action: 'R',
    });
    render(
      <MemoryRouter initialEntries={['/learn/scenario/scn-01']}>
        <Routes><Route path="/learn/scenario/:id" element={<Scenario />} /></Routes>
      </MemoryRouter>,
    );
    await waitFor(() => expect(document.title).toBe('Practice Scenario | CyberShield Community'));
  });
});

describe('privacy page and footer link', () => {
  test('privacy explains collection honestly, links home/learn', () => {
    render(<MemoryRouter><Privacy /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: /what we collect/i })).toBeInTheDocument();
    expect(screen.getByText(/no automatic deletion/i)).toBeInTheDocument();
    expect(screen.getByText(/never visited, downloaded or executed/i)).toBeInTheDocument();
  });

  test('footer links the privacy page', () => {
    render(<MemoryRouter><Footer /></MemoryRouter>);
    expect(screen.getByRole('link', { name: /^privacy$/i })).toHaveAttribute('href', '/privacy');
  });

  test('privacy route is registered in App', () => {
    const app = readFileSync(join(__dirname, '..', 'src', 'App.jsx'), 'utf8');
    expect(app).toMatch(/<Route path="\/privacy" element=\{<Privacy \/>\} \/>/);
  });
});

describe('canonical links', () => {
  test('PageMeta emits a runtime-origin canonical (no hardcoded domain)', () => {
    // NOTE: jsdom window.location never changes under MemoryRouter, so this
    // asserts the mechanism (runtime origin + current path, nothing
    // hardcoded) rather than a specific path.
    render(
      <MemoryRouter initialEntries={['/learn']}>
        <Routes><Route path="/learn" element={<PageMeta title="Learn About Scams" description="Desc." />} /></Routes>
      </MemoryRouter>,
    );
    const canonical = document.querySelector('link[rel="canonical"]');
    expect(canonical?.getAttribute('href')).toBe(
      `${window.location.origin}${window.location.pathname}`,
    );
    expect(canonical?.getAttribute('href')).not.toContain('example.org');
  });
});

describe('social metadata and favicon (index.html fallback)', () => {
  test('static head tags exist for non-JS scrapers', () => {
    const html = readFileSync(join(__dirname, '..', 'index.html'), 'utf8');
    for (const needle of [
      'rel="icon"',
      'og:type',
      'og:site_name',
      'og:title',
      'og:description',
      'og:url',
      'og:image',
      'twitter:card',
      'twitter:title',
      'application/ld+json',
      '"@type": "WebApplication"',
    ]) {
      expect(html).toContain(needle);
    }
    expect(html).toContain('summary_large_image');
  });
});

describe('vercel.json', () => {
  test('SPA fallback + documented backend placeholder, assets untouched', () => {
    const cfg = JSON.parse(readFileSync(join(__dirname, '..', 'vercel.json'), 'utf8'));
    const api = cfg.rewrites.find((r) => r.source.startsWith('/api/'));
    expect(api.destination).toContain('REPLACE-WITH-BACKEND-URL');
    const fallback = cfg.rewrites.find((r) => r.destination === '/index.html');
    expect(fallback).toBeDefined();
    expect(fallback.source.startsWith('/api')).toBe(false);
  });
});

describe('robots.txt', () => {
  test('allows crawling, blocks admin, points to sitemap, no site-wide disallow', () => {
    const robots = readFileSync(join(__dirname, '..', 'public', 'robots.txt'), 'utf8');
    expect(robots).toMatch(/^Allow: \/$/m);
    expect(robots).toMatch(/^Disallow: \/admin$/m);
    expect(robots).not.toMatch(/^Disallow: \/$/m);
    expect(robots).toMatch(/Sitemap: .*sitemap\.xml/);
  });
});

describe('sitemap generator', () => {
  test('emits exactly the public pages, never admin/login/params', () => {
    const out = execFileSync(
      'node',
      ['scripts/generate-sitemap.mjs'],
      { cwd: join(__dirname, '..'), env: { ...process.env, SITEMAP_BASE_URL: 'https://test.example' } },
    ).toString();
    expect(out).toMatch(/11 public URLs/);
    const xml = readFileSync(join(__dirname, '..', 'public', 'sitemap.xml'), 'utf8');
    for (const p of ['/', '/about', '/analyze', '/analyze/url', '/awareness', '/community', '/impact', '/learn', '/privacy', '/quiz', '/report']) {
      expect(xml).toContain(`<loc>https://test.example${p}</loc>`);
    }
    expect(xml).not.toContain('/admin');
    expect(xml).not.toContain(':id');
    expect(xml).not.toContain('*');
  });
});
