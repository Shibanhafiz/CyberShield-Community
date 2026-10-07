import { Link } from 'react-router-dom';
import PageMeta from '../components/PageMeta';
import { Card, Container, PageHeader } from '../components/ui';

function Section({ title, children }) {
  return (
    <Card title={title} className="mt-4">
      <div className="space-y-2 text-sm leading-relaxed text-ink-2">{children}</div>
    </Card>
  );
}

export default function Privacy() {
  return (
    <Container narrow>
      <PageMeta
        title="Privacy"
        description="What CyberShield Community collects, what it never collects, and how your anonymous reports and scores are handled."
      />
      <PageHeader
        eyebrow="Privacy"
        title="What we collect — and what we never do"
        description="CyberShield is anonymous by design: no accounts, no names, no personal details. This page describes exactly what the application does today."
      />

      <Section title="What is collected">
        <p>
          <strong className="text-ink">Redacted message or link text.</strong> Before
          anything is stored, passwords, OTPs, PINs, card numbers, phone numbers
          and email addresses are masked (for example, an OTP becomes
          [REDACTED]). Only this redacted text is kept.
        </p>
        <p>
          <strong className="text-ink">Category, content type, risk level and a
          broad locality</strong> you type yourself (for example a town name —
          never your address), plus an optional description you write.
        </p>
        <p>
          <strong className="text-ink">Analysis metadata only.</strong> When you
          analyze a message or link without reporting it, only the outcome
          (category, risk level, score, indicator codes) is recorded for
          community statistics — never the text or link itself.
        </p>
        <p>
          <strong className="text-ink">Quiz and awareness scores</strong> linked
          to a random session ID stored in your own browser, which identifies
          no one.
        </p>
        <p>
          <strong className="text-ink">Anonymous feedback</strong> (topic,
          1–5 rating, participant category, broad locality, optional comment).
        </p>
      </Section>

      <Section title="What is never collected">
        <p>
          Names, phone numbers, Aadhaar or ID numbers, passwords, OTPs, PINs,
          bank or card details, exact home addresses, GPS coordinates, device
          data, or anything that identifies you. Reviewer accounts store only
          an email address and a password hash.
        </p>
      </Section>

      <Section title="How reports stay anonymous">
        <p>
          Reports carry no identity: duplicates are matched by a SHA-256
          fingerprint of the redacted content, not by who submitted them.
          Public dashboards show only counts and coarse areas — never raw
          report text or individual histories.
        </p>
      </Section>

      <Section title="What analysis results mean">
        <p>
          Risk levels and scores are <strong className="text-ink">heuristic
          indicators to support your decision</strong>, not guaranteed proof
          that something is a scam. URL checks inspect the link’s structure
          only — links are never visited, downloaded or executed.
        </p>
      </Section>

      <Section title="Who can see what">
        <p>
          Public pages show aggregated, anonymous statistics. Individual
          reports and feedback are visible only to authorized project
          reviewers in the admin console, where every status change and
          export is recorded in an audit log.
        </p>
      </Section>

      <Section title="Retention and deletion">
        <p>
          There is currently <strong className="text-ink">no automatic
          deletion</strong>: submitted data is kept until the project team
          removes it, and a formal retention period is still to be defined
          with the field team. If you submitted something by mistake, contact
          the project team that ran your session.
        </p>
      </Section>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/" className="inline-flex h-11 items-center rounded-lg bg-brand px-5 text-sm font-semibold text-white hover:bg-brand-dark">
          Back to home
        </Link>
        <Link to="/learn" className="inline-flex h-11 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
          Learn about scams
        </Link>
      </div>
    </Container>
  );
}
