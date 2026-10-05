import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import LoadingState from '../components/LoadingState';
import QuizRunner from '../components/QuizRunner';
import { Alert, Card, Container, PageHeader } from '../components/ui';
import { getQuizQuestions, getSessionId, submitQuizAttempt } from '../api';

export default function Quiz() {
  const [questions, setQuestions] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    getQuizQuestions('quiz', 20)
      .then((qs) => { if (mounted) setQuestions(qs); })
      .catch(() => { if (mounted) setError('Could not load the quiz. Please try again.'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, []);

  async function handleSubmit(answers) {
    const res = await submitQuizAttempt(getSessionId(), 'quiz', answers);
    setResult(res);
    return res;
  }

  if (loading) {
    return (
      <Container narrow>
        <LoadingState label="Loading quiz…" />
      </Container>
    );
  }

  if (error || !questions) {
    return (
      <Container narrow>
        <Alert tone="error">{error || 'Quiz unavailable.'}</Alert>
      </Container>
    );
  }

  return (
    <Container narrow>
      <PageHeader
        eyebrow="Quiz"
        title="Awareness quiz"
        description={`${questions.length} questions in random order. Answers are checked on the server to keep the quiz fair — review each explanation at the end.`}
      />

      {result && (
        <div className="mt-6 space-y-4">
          <Card title="Your score">
            <p className="text-3xl font-bold text-ink">
              {result.score}<span className="text-base font-medium text-muted">/{result.total}</span>
            </p>
            <div className="mt-4 space-y-1.5">
              <p className="text-[13px] font-semibold uppercase tracking-wider text-muted">Category strengths</p>
              {Object.entries(result.category_scores).map(([cat, t]) => (
                <div key={cat} className="flex items-center justify-between border-b border-line/70 py-1.5 text-sm last:border-b-0">
                  <span className="text-ink-2">{cat}</span>
                  <span className={`font-semibold ${t.correct === t.total ? 'text-ok' : 'text-[#92400e]'}`}>
                    {t.correct}/{t.total}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Topics to review">
            {result.recommendations.length === 0 ? (
              <p className="text-sm font-medium text-ok">
                Excellent — every category fully correct. Consider trying the practice scenarios to stay sharp.
              </p>
            ) : (
              <ul className="space-y-1.5">
                {result.recommendations.map((r) => (
                  <li key={r.slug}>
                    <Link to="/learn" className="text-sm font-medium text-brand-dark hover:underline">
                      • {r.title}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <h2 className="pt-1 text-lg font-bold text-ink">Review your answers</h2>
        </div>
      )}

      <div className="mt-6">
        <QuizRunner questions={questions} submitLabel="See my score" onSubmit={handleSubmit} />
      </div>

      {result && (
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/learn" className="inline-flex h-10 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
            Study topics
          </Link>
          <Link to="/awareness" className="inline-flex h-10 items-center rounded-lg border border-line bg-surface px-5 text-sm font-semibold text-ink hover:border-muted">
            Try before / after assessment
          </Link>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex h-10 items-center rounded-lg bg-brand px-5 text-sm font-semibold text-white hover:bg-brand-dark"
          >
            Retake quiz
          </button>
        </div>
      )}
    </Container>
  );
}
