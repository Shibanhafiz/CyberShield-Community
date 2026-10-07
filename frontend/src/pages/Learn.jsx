import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, CheckCircle2, ChevronDown, FlaskConical, GraduationCap, LineChart, XCircle } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import PageMeta from '../components/PageMeta';
import FeedbackForm from '../components/FeedbackForm';
import { Alert, Button, Card, Container, EmptyState, PageHeader } from '../components/ui';
import { getScenarios, getTopic, getTopics } from '../api';

const flow = [
  { icon: BookOpen, label: 'Learn', text: 'Read short topics' },
  { icon: FlaskConical, label: 'Practice', text: 'Try realistic scenarios' },
  { icon: GraduationCap, label: 'Test', text: 'Take the quiz' },
  { icon: LineChart, label: 'Improve', text: 'Review weak topics' },
];

function TopicCard({ topic }) {
  const [open, setOpen] = useState(false);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  async function toggle() {
    if (open) {
      setOpen(false);
      return;
    }
    setOpen(true);
    if (!detail) {
      setLoading(true);
      try {
        setDetail(await getTopic(topic.slug));
      } catch {
        setDetail({ error: true });
      } finally {
        setLoading(false);
      }
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-line bg-surface shadow-card">
      <button
        onClick={toggle}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left hover:bg-surface-2/60"
      >
        <span>
          <span className="block text-xs font-semibold uppercase tracking-wider text-muted">
            {topic.category}
          </span>
          <span className="mt-0.5 block text-[15px] font-semibold text-ink">{topic.title}</span>
          <span className="mt-1 block text-sm text-ink-2">{topic.description}</span>
        </span>
        <ChevronDown
          size={18}
          className={`shrink-0 text-muted transition-transform ${open ? 'rotate-180' : ''}`}
          aria-hidden
        />
      </button>
      {open && (
        <div className="border-t border-line px-5 py-4 text-sm leading-relaxed">
          {loading && <LoadingState label="Loading topic…" />}
          {detail && detail.error && (
            <p className="text-sm text-bad">Could not load this topic. Please try again.</p>
          )}
          {detail && !detail.error && (
            <div className="space-y-4 text-ink-2">
              <div>
                <p className="font-semibold text-ink">What is it?</p>
                <p className="mt-1">{detail.what_it_is}</p>
              </div>
              <div>
                <p className="font-semibold text-ink">Warning signs</p>
                <ul className="mt-1 list-disc space-y-1 pl-5">
                  {detail.warning_signs.map((w) => <li key={w}>{w}</li>)}
                </ul>
              </div>
              <div className="rounded-lg border border-line bg-surface-2/60 p-3.5">
                <p className="font-semibold text-ink">Example (fictional)</p>
                <p className="mt-1">{detail.example}</p>
                <p className="mt-2 text-[13px] text-muted">
                  Attacker&apos;s goal: {detail.attacker_goal}
                </p>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg border border-ok/30 bg-ok-tint p-3.5">
                  <p className="flex items-center gap-1.5 font-semibold text-ok">
                    <CheckCircle2 size={14} aria-hidden /> Do this
                  </p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-[13px]">
                    {detail.should_do.map((d) => <li key={d}>{d}</li>)}
                  </ul>
                </div>
                <div className="rounded-lg border border-bad/30 bg-bad-tint p-3.5">
                  <p className="flex items-center gap-1.5 font-semibold text-bad">
                    <XCircle size={14} aria-hidden /> Never do this
                  </p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-[13px]">
                    {detail.never_do.map((d) => <li key={d}>{d}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function Learn() {
  const [topics, setTopics] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([getTopics(), getScenarios()])
      .then(([t, s]) => {
        if (mounted) {
          setTopics(t);
          setScenarios(s);
        }
      })
      .catch(() => {
        if (mounted) setError('Learning content is temporarily unavailable. Please try again later.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <Container>
        <LoadingState label="Loading learning center…" />
      </Container>
    );
  }

  if (error) {
    return (
      <Container narrow>
        <Alert tone="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <PageMeta
        title="Learn About Scams"
        description="Short plain-language lessons on phishing, OTP fraud and more, with practice scenarios, quizzes and anonymous feedback."
      />
      <PageHeader
        eyebrow="Learn"
        title="Cyber safety learning center"
        description="Short lessons, realistic practice scenarios and quizzes — written in plain language for everyone. No accounts, no personal data."
      />

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {flow.map((f) => (
          <div key={f.label} className="rounded-xl border border-line bg-surface p-4 text-center shadow-card">
            <f.icon size={20} className="mx-auto text-brand" aria-hidden />
            <p className="mt-1.5 text-sm font-semibold text-ink">{f.label}</p>
            <p className="text-xs text-muted">{f.text}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/quiz" className="inline-flex h-10 items-center rounded-lg bg-brand px-5 text-sm font-semibold text-white hover:bg-brand-dark">
          Take the quiz
        </Link>
        <Link to="/awareness" className="inline-flex h-10 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
          Before / after assessment
        </Link>
        <Link to="/impact" className="inline-flex h-10 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
          Community impact
        </Link>
      </div>

      <h2 className="mt-10 text-lg font-bold text-ink">Topics</h2>
      <div className="mt-3 space-y-3">
        {topics.map((t) => <TopicCard key={t.slug} topic={t} />)}
      </div>

      <h2 className="mt-10 text-lg font-bold text-ink">
        Practice scenarios ({scenarios.length})
      </h2>
      <p className="mt-1 text-[13px] text-muted">
        Fictional messages for practice. Never contact real senders or open real suspicious links.
      </p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {scenarios.map((s) => (
          <Link
            key={s.scenario_id}
            to={`/learn/scenario/${s.scenario_id}`}
            className="block rounded-xl border border-line bg-surface p-4 shadow-card hover:border-brand/50"
          >
            <p className="text-xs font-semibold uppercase tracking-wider text-muted">
              {s.category} · {s.difficulty}
            </p>
            <p className="mt-1 text-[15px] font-semibold text-ink">{s.title}</p>
            <p className="mt-1.5 text-sm font-semibold text-brand-dark">Practice this →</p>
          </Link>
        ))}
      </div>

      <div className="mt-10 max-w-2xl">
        <Card title="Share anonymous feedback">
          <FeedbackForm />
        </Card>
      </div>
    </Container>
  );
}
