import { useState } from 'react';
import { Button } from './ui';

/**
 * Generic multiple-choice runner: answer all questions (progress bar),
 * submit once for server-side scoring, then review each answer with its
 * explanation. Correct answers are never on the client before submit.
 */
export default function QuizRunner({ questions, submitLabel, onSubmit }) {
  const [index, setIndex] = useState(0);
  const [picked, setPicked] = useState({});
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const q = questions[index];
  const answered = Object.keys(picked).length;

  function choose(opt) {
    if (result) return;
    setPicked((p) => ({ ...p, [q.id]: opt }));
  }

  async function submit() {
    setSubmitting(true);
    setError('');
    try {
      const answers = questions.map((x) => ({ question_id: x.id, selected: picked[x.id] ?? -1 }));
      setResult(await onSubmit(answers));
    } catch {
      setError('Could not submit your answers. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  if (result) {
    const byId = Object.fromEntries(result.results.map((r) => [r.question_id, r]));
    return (
      <div>
        {result.results && (
          <div className="space-y-3">
            {questions.map((x, i) => {
              const r = byId[x.id];
              const ok = r && r.correct;
              return (
                <div key={x.id} className={`rounded-xl border p-4 ${ok ? 'border-ok/40 bg-ok-tint' : 'border-bad/30 bg-bad-tint'}`}>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted">
                    Q{i + 1} · {x.category} — {ok ? 'Correct' : 'Incorrect'}
                  </p>
                  <p className="mt-1 text-sm font-semibold text-ink">{x.question}</p>
                  <p className="mt-1 text-[13px] text-ink-2">
                    Your answer: {picked[x.id] >= 0 ? x.options[picked[x.id]] : '—'}
                  </p>
                  <p className="mt-1 text-[13px] leading-relaxed text-ink-2">{r && r.explanation}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between text-sm text-muted">
        <span>Question {index + 1} / {questions.length}</span>
        <span>{answered} answered</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-2" role="progressbar" aria-valuenow={index + 1} aria-valuemin={1} aria-valuemax={questions.length} aria-label={`Question ${index + 1} of ${questions.length}`}>
        <div className="h-full bg-brand transition-all" style={{ width: `${((index + 1) / questions.length) * 100}%` }} />
      </div>

      <div className="mt-4 rounded-xl border border-line bg-surface p-5 shadow-card">
        <p className="text-xs font-semibold uppercase tracking-wider text-brand-dark">{q.category}</p>
        <p className="mt-1 font-semibold text-ink">{q.question}</p>
        <div className="mt-3 space-y-2" role="group" aria-label={`Answer choices for question ${index + 1}`}>
          {q.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => choose(i)}
              aria-pressed={picked[q.id] === i}
              className={`min-h-[48px] w-full rounded-lg border px-4 py-3 text-left text-[15px] transition-colors ${
                picked[q.id] === i
                  ? 'border-brand bg-brand-tint font-medium text-ink'
                  : 'border-line bg-surface text-ink-2 hover:border-brand/50'
              }`}
            >
              <span className="mr-2 font-bold text-brand-dark" aria-hidden>{String.fromCharCode(65 + i)}.</span>
              {opt}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <Button
          variant="secondary"
          onClick={() => setIndex((v) => Math.max(0, v - 1))}
          disabled={index === 0}
        >
          ← Back
        </Button>
        {index < questions.length - 1 ? (
          <Button variant="secondary" onClick={() => setIndex((v) => v + 1)}>
            Next →
          </Button>
        ) : (
          <Button
            onClick={submit}
            disabled={submitting || answered < questions.length}
            title={answered < questions.length ? `Answer all questions (${answered}/${questions.length})` : 'Submit for scoring'}
          >
            {submitting ? 'Checking…' : submitLabel}
          </Button>
        )}
      </div>
      {error && (
        <p className="mt-3 rounded-lg border border-bad/30 bg-bad-tint px-4 py-2.5 text-sm text-bad" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
