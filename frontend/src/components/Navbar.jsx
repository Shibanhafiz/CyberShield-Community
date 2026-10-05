import { useEffect, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, ShieldCheck, X } from 'lucide-react';

export const publicLinks = [
  { to: '/', label: 'Home', end: true },
  { to: '/analyze', label: 'Check Message' },
  { to: '/analyze/url', label: 'Check URL' },
  { to: '/community', label: 'Community' },
  { to: '/learn', label: 'Learn' },
  { to: '/quiz', label: 'Quiz' },
];

const extraLinks = [
  { to: '/report', label: 'Report a Scam' },
  { to: '/awareness', label: 'Awareness Check' },
  { to: '/impact', label: 'Community Impact' },
  { to: '/about', label: 'About' },
];

function desktopClass({ isActive }) {
  return `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive ? 'bg-brand-tint text-brand-dark' : 'text-ink-2 hover:bg-surface-2 hover:text-ink'
  }`;
}

export default function Navbar({ backendStatus }) {
  const [open, setOpen] = useState(false);
  const online = backendStatus === 'online';

  // Close on Escape + lock background scroll while the menu is open.
  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
  }, [open ]);

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-surface">
      <div className="mx-auto flex h-16 w-full max-w-[1200px] items-center justify-between gap-3 px-4 sm:px-6">
        <Link to="/" className="flex min-h-[44px] items-center gap-2.5" onClick={() => setOpen(false)}>
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-white" aria-hidden>
            <ShieldCheck size={18} />
          </span>
          <span className="leading-tight">
            <span className="block text-[15px] font-bold tracking-tight text-ink">CyberShield</span>
            <span className="block text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">
              Community cyber safety
            </span>
          </span>
        </Link>

        <nav aria-label="Primary" className="hidden items-center gap-0.5 lg:flex">
          {publicLinks.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={desktopClass}>
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2.5">
          <span
            title={online ? 'Backend reachable' : 'Backend unreachable'}
            className={`hidden items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium sm:inline-flex ${
              online ? 'border-ok/30 bg-ok-tint text-ok' : 'border-warn/40 bg-warn-tint text-[#92400e]'
            }`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${online ? 'bg-ok' : 'bg-warn'}`} aria-hidden />
            {online ? 'Service online' : 'Service offline'}
          </span>
          <Link
            to="/report"
            className="hidden h-11 items-center rounded-lg bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark sm:inline-flex"
          >
            Report a scam
          </Link>
          <button
            type="button"
            onClick={() => setOpen(true)}
            aria-label="Open menu"
            className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-line text-ink hover:bg-surface-2 lg:hidden"
          >
            <Menu size={20} aria-hidden />
          </button>
        </div>
      </div>

      {/* Full-screen mobile menu: large targets, easy close, keyboard safe. */}
      {open && (
        <div className="fixed inset-0 z-50 flex flex-col bg-surface lg:hidden" role="dialog" aria-modal="true" aria-label="Site menu">
          <div className="flex h-16 items-center justify-between border-b border-line px-4">
            <span className="flex items-center gap-2.5">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-white" aria-hidden>
                <ShieldCheck size={18} />
              </span>
              <span className="text-[15px] font-bold text-ink">CyberShield</span>
            </span>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close menu"
              autoFocus
              className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-line text-ink hover:bg-surface-2"
            >
              <X size={20} aria-hidden />
            </button>
          </div>
          <nav aria-label="Mobile" className="flex-1 overflow-y-auto px-4 py-3">
            {[...publicLinks, ...extraLinks].map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `flex min-h-[52px] items-center rounded-lg px-3 text-base font-semibold ${
                    isActive ? 'bg-brand-tint text-brand-dark' : 'text-ink hover:bg-surface-2'
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
          <div className="border-t border-line px-4 py-4">
            <p className="text-center text-xs text-muted">
              {online ? 'Service online' : 'Service offline'} · Assessments are indicative only
            </p>
          </div>
        </div>
      )}
    </header>
  );
}
