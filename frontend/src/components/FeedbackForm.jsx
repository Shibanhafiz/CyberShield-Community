import { useState } from 'react';
import LoadingState from './LoadingState';
import { Button, Field, Select, TextArea, TextInput } from './ui';
import { getSessionId, submitFeedback } from '../api';

const CATEGORIES = [
  'Student',
  'Farmer',
  'Senior Citizen',
  'Small Business Owner',
  'General Community Member',
  'Other',
];

/** Anonymous field-study feedback form (no identities collected). */
export default function FeedbackForm({ topic: fixedTopic }) {
  const [topic, setTopic] = useState(fixedTopic || '');
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [category, setCategory] = useState('');
  const [locality, setLocality] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please say which topic this feedback is about.');
      return;
    }
    if (rating < 1 || rating > 5) {
      setError('Please choose a rating from 1 to 5.');
      return;
    }
    setSending(true);
    setError('');
    try {
      await submitFeedback({
        session_id: getSessionId(),
        topic: topic.trim().slice(0, 128),
        rating,
        feedback: feedback.trim().slice(0, 2000) || undefined,
        participant_category: category || undefined,
        broad_locality: locality.trim().slice(0, 100) || undefined,
      });
      setDone(true);
    } catch {
      setError('Could not send feedback. Please try again later.');
    } finally {
      setSending(false);
    }
  }

  if (done) {
    return (
      <div className="rounded-lg border border-ok/30 bg-ok-tint p-5 text-center" role="status">
        <p className="font-semibold text-ok">Thank you for your feedback!</p>
        <p className="mt-1 text-[13px] text-ink-2">Your anonymous response helps improve community awareness material.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-[13px] text-muted">
        Optional and anonymous. Never include names, phone numbers, OTPs or other personal details.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Topic" htmlFor="fb-topic">
          <TextInput
            id="fb-topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. OTP & banking scams"
            maxLength={128}
          />
        </Field>
        <Field label="I am a… (optional)" htmlFor="fb-category">
          <Select id="fb-category" value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">Prefer not to say</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </Select>
        </Field>
      </div>
      <div>
        <span className="block text-sm font-medium text-ink" id="fb-rating-label">Rating</span>
        <div className="mt-1.5 flex gap-1.5" role="radiogroup" aria-labelledby="fb-rating-label">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              role="radio"
              aria-checked={rating === n}
              aria-label={`${n} out of 5`}
              onClick={() => setRating(n)}
              className={`h-9 w-9 rounded-lg border text-sm font-semibold transition-colors ${
                rating === n
                  ? 'border-warn bg-warn-tint text-[#92400e]'
                  : 'border-line text-ink-2 hover:border-warn'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Broad locality (optional)" htmlFor="fb-locality">
          <TextInput
            id="fb-locality"
            value={locality}
            onChange={(e) => setLocality(e.target.value)}
            placeholder="e.g. Bhatkal area"
            maxLength={100}
          />
        </Field>
        <Field label="Comments (optional)" htmlFor="fb-comments">
          <TextArea
            id="fb-comments"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={2}
            maxLength={2000}
            placeholder="What helped? What was confusing?"
          />
        </Field>
      </div>
      {sending && <LoadingState label="Sending…" />}
      {error && (
        <p className="rounded-lg border border-bad/30 bg-bad-tint px-4 py-2.5 text-sm text-bad" role="alert">
          {error}
        </p>
      )}
      <Button type="submit" disabled={sending}>
        {sending ? 'Sending…' : 'Submit anonymous feedback'}
      </Button>
    </form>
  );
}
