import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import LoadingState from '../components/LoadingState';
import PageMeta from '../components/PageMeta';
import QuizRunner from '../components/QuizRunner';
import { Alert, Button, Card, Container, PageHeader } from '../components/ui';
import {
  getAwarenessSession,
  getQuizQuestions,
  getSessionId,
  submitAfter,
  submitBefore,
} from '../api';

const steps = ['Before assessment', 'Learn', 'After assessment'];

export default function Awareness() {
  const [sessionId] = useState(getSessionId);
  const [questions, setQuestions] = useState(null);
  const [stage, setStage] = useState('before'); // before | learn | after | done
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([getQuizQuestions('assessment', 6), getAwarenessSession(sessionId).catch(() => null)])
      .then(([qs, sess]) => {
        if (!mounted) return;
        setQuestions(qs);
        if (sess && sess.after_score != null) {
          setSession(sess);
          setStage('done');
        } else if (sess && sess.before_score != null) {
          setSession(sess);
          setStage('learn');
        }
      })
      .catch(() => {
        if (mounted) setError('Could not load the assessment. Please try again.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [sessionId]);

  async function handleBefore(answers) {
    const res = await submitBefore(sessionId, answers);
    setSession(res.session);
    setStage('learn');
    return res;
  }

  async function handleAfter(answers) {
    const res = await submitAfter(sessionId, answers);
    setSession(res.session);
    setStage('done');
    return res;
  }

  if (loading) {
    return (
      <Container narrow>
        <LoadingState label="Loading assessment…" />
      </Container>
    );
  }

  if (error || !questions || questions.length === 0) {
    return (
      <Container narrow>
        <Alert tone="error">{error || 'Assessment unavailable.'}</Alert>
      </Container>
    );
  }

  const activeIdx = stage === 'before' ? 0 : stage === 'learn' ? 1 : 2;

  return (
    <Container narrow>
      <PageMeta
        title="Before / After Assessment"
        description="Answer 6 questions, study the learning material, then answer again to see how your awareness score changed."
      />
      <PageHeader
        eyebrow="Awareness"
        title="Before / After Assessment"
        description="Answer 6 questions, explore the learning material, then answer again. Anonymous — your session ID is random and identifies no one."
      />
      <p className="mt-2 font-mono text-xs text-muted">session: {sessionId.slice(0, 8)}…</p>

      <div className="mt-5 flex gap-2" aria-label="Progress">
        {steps.map((s, i) => (
          <div
            key={s}
            aria-current={i === activeIdx ? 'step' : undefined}
            className={`flex-1 rounded-lg px-2 py-2 text-center text-xs font-semibold ${
              i < activeIdx
                ? 'bg-ok-tint text-ok'
                : i === activeIdx
                  ? 'bg-brand text-white'
                  : 'bg-surface-2 text-muted'
            }`}
          >
            {i + 1}. {s}
          </div>
        ))}
      </div>

      {stage === 'before' && (
        <div className="mt-6">
          <h2 className="text-lg font-bold text-ink">Step 1 — Before assessment</h2>
          <p className="mt-1 text-[13px] text-muted">Answer from what you know right now.</p>
          <div className="mt-4">
            <QuizRunner key="before" questions={questions} submitLabel="Save & Continue to Learning" onSubmit={handleBefore} />
          </div>
        </div>
      )}

      {stage === 'learn' && (
        <Card className="mt-6 text-center" title="Before score saved">
          <p className="text-sm text-ink-2">
            {session && session.before_score != null && (
              <>You scored <span className="font-bold text-ink">{session.before_score}/{session.before_total}</span>. </>
            )}
            Now explore the material, then take the after assessment.
          </p>
          <div className="mt-4 flex flex-wrap justify-center gap-3">
            <Link to="/learn" className="inline-flex h-10 items-center rounded-lg bg-brand px-5 text-sm font-semibold text-white hover:bg-brand-dark">
              Open Learning Center
            </Link>
            <Button variant="secondary" onClick={() => setStage('after')}>
              I Have Studied — Start After Assessment
            </Button>
          </div>
        </Card>
      )}

      {stage === 'after' && (
        <div className="mt-6">
          <h2 className="text-lg font-bold text-ink">Step 3 — After assessment</h2>
          <p className="mt-1 text-[13px] text-muted">Same 6 questions, answered after studying.</p>
          <div className="mt-4">
            <QuizRunner key="after" questions={questions} submitLabel="See My Change" onSubmit={handleAfter} />
          </div>
        </div>
      )}

      {stage === 'done' && session && (
        <div className="mt-6 space-y-4">
          <Card title="Awareness assessment result">
            <div className="text-center">
              <p className="text-sm text-ink-2">
                Before: <span className="font-bold text-ink">{session.before_score}/{session.before_total}</span>
                {'  →  '}After: <span className="font-bold text-ink">{session.after_score}/{session.after_total}</span>
              </p>
              <p className="mt-2 text-xl font-bold text-ink">
                Your awareness quiz score changed by{' '}
                {(session.score_difference >= 0 ? '+' : '') + session.score_difference} point{Math.abs(session.score_difference ?? 0) === 1 ? '' : 's'}.
              </p>
              <p className="mx-auto mt-2 max-w-md text-xs text-muted">
                An awareness exercise, not a safety guarantee — staying cautious matters more than any score.
              </p>
            </div>
          </Card>
          <div className="flex flex-wrap justify-center gap-3">
            <Link to="/learn" className="inline-flex h-10 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
              Keep learning
            </Link>
            <Link to="/impact" className="inline-flex h-10 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
              See community impact
            </Link>
          </div>
        </div>
      )}
    </Container>
  );
}
