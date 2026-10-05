import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LogOut, ShieldCheck } from 'lucide-react';
import LoadingState from '../../components/LoadingState';
import { Button } from '../../components/ui';
import { adminMe, clearAdminToken, getAdminProfile, getAdminToken } from '../../api';

const links = [
  { to: '/admin', label: 'Dashboard', end: true },
  { to: '/admin/reports', label: 'Reports' },
  { to: '/admin/analytics', label: 'Analytics' },
  { to: '/admin/awareness', label: 'Awareness' },
  { to: '/admin/feedback', label: 'Feedback' },
  { to: '/admin/exports', label: 'Exports' },
  { to: '/admin/audit', label: 'Audit logs' },
];

function linkClass({ isActive }) {
  return `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive ? 'bg-brand-tint text-brand-dark' : 'text-ink-2 hover:bg-surface-2 hover:text-ink'
  }`;
}

export function useAdminGuard() {
  const navigate = useNavigate();
  const [state, setState] = useState({ loading: true, profile: null });

  useEffect(() => {
    let mounted = true;
    if (!getAdminToken()) {
      navigate('/admin/login', { replace: true });
      return;
    }
    adminMe()
      .then((profile) => {
        if (mounted) setState({ loading: false, profile });
      })
      .catch(() => {
        clearAdminToken();
        if (mounted) navigate('/admin/login', { replace: true });
      });
    return () => { mounted = false; };
  }, [navigate]);

  return state;
}

export default function AdminLayout() {
  const { loading, profile } = useAdminGuard();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1200px] px-4 py-10 sm:px-6">
        <LoadingState label="Verifying admin session…" />
      </div>
    );
  }

  function logout() {
    clearAdminToken();
    navigate('/admin/login', { replace: true });
  }

  const nav = (
    <nav aria-label="Admin" className="space-y-0.5">
      {links.map((l) => (
        <NavLink key={l.to} to={l.to} end={l.end} className={linkClass} onClick={() => setMenuOpen(false)}>
          {l.label}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="mx-auto w-full max-w-[1200px] px-4 sm:px-6">
      <div className="flex items-center justify-between gap-3 border-b border-line pb-4">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-ink text-white" aria-hidden>
            <ShieldCheck size={18} />
          </span>
          <div>
            <p className="text-[15px] font-bold tracking-tight text-ink">Admin console</p>
            <p className="text-xs text-muted">
              {profile ? `${profile.email} · ${profile.role}` : 'Internal tool'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setMenuOpen((v) => !v)}
            aria-expanded={menuOpen}
            className="h-9 rounded-lg border border-line px-3 text-sm font-semibold text-ink md:hidden"
          >
            Menu
          </button>
          <Button variant="secondary" onClick={logout} className="h-9">
            <LogOut size={14} aria-hidden /> Log out
          </Button>
        </div>
      </div>

      <div className="mt-5 grid gap-6 md:grid-cols-[210px_1fr]">
        <aside className="hidden md:block">
          <div className="sticky top-20 rounded-xl border border-line bg-surface p-2.5 shadow-card">
            {nav}
            <p className="mt-3 border-t border-line px-3 pt-3 text-xs leading-relaxed text-muted">
              Reviewer identities are never shown publicly. Actions are audit-logged.
            </p>
          </div>
        </aside>
        {menuOpen && (
          <div className="rounded-xl border border-line bg-surface p-2.5 md:hidden">
            {nav}
          </div>
        )}
        <div className="min-w-0">
          <Outlet context={{ profile }} />
        </div>
      </div>
    </div>
  );
}

export function AdminProfileName() {
  const profile = getAdminProfile();
  return <span>{profile ? profile.email : 'admin'}</span>;
}
