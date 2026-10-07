import { Link } from 'react-router-dom';
import PageMeta from '../components/PageMeta';
import { Container } from '../components/ui';

const steps = [
  { n: '1', title: 'Paste', text: 'Submit a suspicious SMS, WhatsApp message, email or URL.' },
  { n: '2', title: 'Analyze', text: 'We check it against common scam indicators and explain what we find.' },
  { n: '3', title: 'Understand', text: 'See why it was flagged — urgency, requests, impersonation patterns.' },
  { n: '4', title: 'Act safely', text: 'Get a recommended next step, and report the pattern if you choose.' },
];

const topics = [
  { title: 'Phishing', text: 'Fake messages and links that steal logins.' },
  { title: 'Banking scams', text: 'KYC and account-suspension scares.' },
  { title: 'OTP scams', text: 'One-time-password theft tactics.' },
  { title: 'Job scams', text: 'Fake offers demanding advance fees.' },
  { title: 'Investment scams', text: 'Guaranteed-return fraud.' },
  { title: 'Digital arrest', text: 'Fake police threats with payment demands.' },
];

export default function Home() {
  return (
    <div>
      <PageMeta
        title="Check before you trust"
        description="CyberShield Community helps you check suspicious messages and links, learn how scams work, and report scam patterns to protect your community."
      />
      {/* Hero */}
      <section className="border-b border-line bg-surface">
        <Container>
          <div className="grid gap-10 py-12 md:grid-cols-2 md:py-16">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-brand-dark">
                Community cyber safety
              </p>
              <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink md:text-4xl">
                Check before you trust.
              </h1>
              <p className="mt-3 max-w-md text-[15px] leading-relaxed text-ink-2">
                Analyze suspicious messages and links for common scam indicators
                and learn what to do next.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  to="/analyze"
                  className="inline-flex h-11 items-center rounded-lg bg-brand px-5 text-[15px] font-semibold text-white hover:bg-brand-dark"
                >
                  Check a message
                </Link>
                <Link
                  to="/analyze/url"
                  className="inline-flex h-11 items-center rounded-lg border border-line bg-surface px-5 text-[15px] font-semibold text-ink hover:border-muted"
                >
                  Check a URL
                </Link>
              </div>
              <p className="mt-4 text-[13px] leading-relaxed text-muted">
                Do not enter passwords, OTPs, PINs, card numbers, or other
                sensitive information.
              </p>
            </div>

            {/* Realistic product preview (static example, not live data) */}
            <div className="rounded-xl border border-line bg-paper p-5 shadow-card" aria-label="Example analysis output">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Example output</p>
              <div className="mt-3 rounded-lg border border-line bg-surface p-4">
                <p className="text-sm italic leading-relaxed text-ink-2">
                  “Your account will be suspended. Update your KYC immediately
                  using this link.”
                </p>
              </div>
              <p className="mt-3 text-sm font-semibold text-ink">Several scam indicators were detected.</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-2">
                <li>Requests sensitive information</li>
                <li>Creates urgency</li>
                <li>Uses account-related threats</li>
              </ul>
              <p className="mt-3 border-t border-line pt-3 text-[13px] text-muted">
                Example only — your results will appear here after analysis, with
                a recommended safe action.
              </p>
            </div>
          </div>
        </Container>
      </section>

      {/* Steps */}
      <section>
        <Container>
          <div className="py-12">
            <h2 className="text-xl font-bold tracking-tight text-ink">How it works</h2>
            <ol className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {steps.map((s) => (
                <li key={s.n} className="rounded-xl border border-line bg-surface p-5 shadow-card">
                  <span
                    className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-brand-tint text-sm font-bold text-brand-dark"
                    aria-hidden
                  >
                    {s.n}
                  </span>
                  <p className="mt-3 text-[15px] font-semibold text-ink">{s.title}</p>
                  <p className="mt-1 text-sm leading-relaxed text-ink-2">{s.text}</p>
                </li>
              ))}
            </ol>
          </div>
        </Container>
      </section>

      {/* Topic rows + community links */}
      <section className="border-t border-line bg-surface">
        <Container>
          <div className="py-10 md:py-12">
            <h2 className="text-xl font-bold tracking-tight text-ink">Protect yourself from common scams</h2>
            <p className="mt-1 text-sm text-ink-2">Short lessons for each pattern — no account needed.</p>
            <ul className="mt-4 divide-y divide-line rounded-xl border border-line bg-paper">
              {topics.map((t) => (
                <li key={t.title}>
                  <Link to="/learn" className="flex min-h-[56px] items-center justify-between gap-3 px-4 py-3">
                    <span className="min-w-0">
                      <span className="block text-[15px] font-semibold text-ink">{t.title}</span>
                      <span className="block truncate text-[13px] text-muted">{t.text}</span>
                    </span>
                    <span className="shrink-0 text-sm font-semibold text-brand-dark" aria-hidden>Learn →</span>
                  </Link>
                </li>
              ))}
            </ul>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Link to="/community" className="flex min-h-[52px] items-center justify-between rounded-xl border border-line bg-paper px-4">
                <span className="text-[15px] font-semibold text-ink">Community reports</span>
                <span className="text-sm font-semibold text-brand-dark" aria-hidden>View →</span>
              </Link>
              <Link to="/quiz" className="flex min-h-[52px] items-center justify-between rounded-xl border border-line bg-paper px-4">
                <span className="text-[15px] font-semibold text-ink">Awareness quiz</span>
                <span className="text-sm font-semibold text-brand-dark" aria-hidden>Start →</span>
              </Link>
            </div>
            <p className="mt-6 max-w-2xl text-[13px] leading-relaxed text-muted">
              Assessments are indicative only and never absolute proof. Community
              figures come from real submitted data — when there is none yet, we
              say so instead of showing estimates.
            </p>
          </div>
        </Container>
      </section>
    </div>
  );
}
