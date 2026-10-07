import { Link } from 'react-router-dom';
import { Button, Container, PageHeader } from '../components/ui';
import PageMeta from '../components/PageMeta';

const links = [
  { to: '/', title: 'Home', text: 'Start from the homepage.' },
  { to: '/analyze', title: 'Check a message', text: 'Analyze a suspicious text.' },
  { to: '/analyze/url', title: 'Check a URL', text: 'Inspect a suspicious link.' },
  { to: '/community', title: 'Community', text: 'See community-reported patterns.' },
  { to: '/learn', title: 'Learn', text: 'Short lessons on common scams.' },
  { to: '/quiz', title: 'Quiz', text: 'Test your scam awareness.' },
];

export default function NotFound() {
  return (
    <Container narrow>
      <PageMeta
        title="Page Not Found"
        description="The page you asked for does not exist. Find what you need on CyberShield Community."
      />
      <PageHeader
        eyebrow="Error 404"
        title="Page not found"
        description="The address may be mistyped, or the page may have moved. Try one of these instead:"
      />
      <ul className="mt-6 divide-y divide-line rounded-xl border border-line bg-surface shadow-card">
        {links.map((l) => (
          <li key={l.to}>
            <Link to={l.to} className="flex min-h-[56px] items-center justify-between gap-3 px-4 py-3">
              <span className="min-w-0">
                <span className="block text-[15px] font-semibold text-ink">{l.title}</span>
                <span className="block truncate text-[13px] text-muted">{l.text}</span>
              </span>
              <span className="shrink-0 text-sm font-semibold text-brand-dark" aria-hidden>→</span>
            </Link>
          </li>
        ))}
      </ul>
      <div className="mt-6">
        <Link to="/">
          <Button>Back to home</Button>
        </Link>
      </div>
    </Container>
  );
}
