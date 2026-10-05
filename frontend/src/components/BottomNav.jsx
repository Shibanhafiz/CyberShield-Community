import { NavLink, useLocation } from 'react-router-dom';
import { BookOpen, Home, ScanSearch, Users } from 'lucide-react';

const items = [
  { to: '/', label: 'Home', end: true, Icon: Home },
  { to: '/analyze', label: 'Check', Icon: ScanSearch },
  { to: '/community', label: 'Community', Icon: Users },
  { to: '/learn', label: 'Learn', Icon: BookOpen },
];

/** Thumb-friendly primary navigation for small screens (max 4 items).
 * Hidden on admin routes — the admin console keeps its own navigation. */
export default function BottomNav() {
  const { pathname } = useLocation();
  if (pathname.startsWith('/admin')) return null;

  return (
    <nav
      aria-label="Primary mobile"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface md:hidden"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      <div className="grid grid-cols-4">
        {items.map(({ to, label, end, Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex min-h-[60px] flex-col items-center justify-center gap-1 text-[11px] font-semibold ${
                isActive ? 'text-brand-dark' : 'text-muted'
              }`
            }
          >
            <Icon size={21} aria-hidden />
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
