import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-line bg-surface">
      <div className="mx-auto grid w-full max-w-[1200px] gap-8 px-4 py-10 sm:px-6 md:grid-cols-3">
        <div>
          <p className="text-sm font-bold text-ink">CyberShield Community</p>
          <p className="mt-2 max-w-sm text-sm leading-relaxed text-ink-2">
            Check suspicious messages and links, learn how scams work, and help
            the community track emerging patterns. Assessments are indicative
            only — always verify through official channels.
          </p>
        </div>
        <nav aria-label="Product" className="text-sm">
          <p className="font-semibold text-ink">Product</p>
          <ul className="mt-2 space-y-1.5 text-ink-2">
            <li><Link className="hover:text-brand-dark hover:underline" to="/analyze">Check a message</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/analyze/url">Check a URL</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/report">Report a scam</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/learn">Learn about scams</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/quiz">Awareness quiz</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/awareness">Before / after assessment</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/impact">Community impact</Link></li>
          </ul>
        </nav>
        <nav aria-label="Project" className="text-sm">
          <p className="font-semibold text-ink">Project</p>
          <ul className="mt-2 space-y-1.5 text-ink-2">
            <li><Link className="hover:text-brand-dark hover:underline" to="/about">About &amp; VTU 1BCP308</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/community">Community dashboard</Link></li>
            <li><Link className="hover:text-brand-dark hover:underline" to="/admin">Admin console</Link></li>
          </ul>
        </nav>
      </div>
      <div className="border-t border-line py-4 text-center text-xs text-muted">
        Awareness content is educational — it does not guarantee protection from scams.
      </div>
    </footer>
  );
}
