import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import { Alert, Button, Card, Container, Field, PageHeader, Select, TextArea, TextInput } from '../components/ui';
import { apiErrorMessage, submitReport } from '../api';

const CATEGORIES = [
  'PHISHING', 'BANKING_SCAM', 'JOB_SCAM', 'INVESTMENT_SCAM', 'DELIVERY_SCAM',
  'OTP_SCAM', 'DIGITAL_ARREST', 'FAKE_SUPPORT', 'OTHER_SCAM', 'NORMAL',
];

export default function Report() {
  const location = useLocation();
  const navigate = useNavigate();
  const prefill = location.state || {};

  const [category, setCategory] = useState(prefill.category || 'PHISHING');
  const [contentType, setContentType] = useState(prefill.contentType || 'message');
  const [content, setContent] = useState(prefill.content || '');
  const [area, setArea] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!content.trim()) {
      setError('Please paste the suspicious content you want to report.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await submitReport({
        content_type: contentType,
        category,
        content: content.trim().slice(0, 10000),
        approximate_area: area.trim() || undefined,
        description: description.trim() || undefined,
      });
      setDone(res);
    } catch (err) {
      const status = err?.response?.status;
      setError(apiErrorMessage(
        err,
        status === 429
          ? 'Too many reports from this address. Please try again later.'
          : 'We couldn’t submit your report. Please try again.',
      ));
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <Container narrow>
        <div className="rounded-xl border border-line bg-surface px-6 py-10 text-center shadow-card">
          <CheckCircle2 size={40} className="mx-auto text-ok" aria-hidden />
          <h1 className="mt-3 text-xl font-bold text-ink">Report submitted</h1>
          <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-ink-2">
            {done.duplicate
              ? 'This appears similar to a previously reported message. Thank you — your submission strengthens the existing community signal.'
              : 'Thank you for helping the community identify emerging scam patterns.'}
          </p>
          <p className="mt-2 text-xs text-muted">
            Community reports are anonymized observations, not verified findings.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Button onClick={() => navigate('/community')}>
              View community dashboard
            </Button>
            <Button variant="secondary" onClick={() => navigate('/analyze')}>
              Analyze another
            </Button>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container narrow>
      <PageHeader
        eyebrow="Report"
        title="Report a scam"
        description={`Share an anonymized report so the community can track emerging patterns.${prefill.fromAnalysis ? ' Details from your analysis are pre-filled — review before submitting.' : ''}`}
      />

      <Alert tone="warning" className="mt-4">
        Do not include passwords, OTPs, card numbers or other sensitive information.
        Sensitive values are masked automatically, but please remove them yourself first.
      </Alert>

      <Card className="mt-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Scam category" htmlFor="rep-category">
              <Select id="rep-category" value={category} onChange={(e) => setCategory(e.target.value)}>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </Select>
            </Field>
            <Field label="Content type" htmlFor="rep-type">
              <Select id="rep-type" value={contentType} onChange={(e) => setContentType(e.target.value)}>
                <option value="message">Message</option>
                <option value="url">URL</option>
              </Select>
            </Field>
          </div>

          <Field
            label="Suspicious content"
            htmlFor="rep-content"
            hint={`${content.length} / 10000 characters`}
          >
            <TextArea
              id="rep-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
              maxLength={10000}
              placeholder="Paste the suspicious message or URL (without secrets)…"
            />
          </Field>

          <Field label="Approximate locality / area (optional)" htmlFor="rep-area">
            <TextInput
              id="rep-area"
              value={area}
              onChange={(e) => setArea(e.target.value)}
              maxLength={100}
              placeholder="e.g. Bhatkal — locality only, never your address"
            />
          </Field>

          <Field label="Description (optional)" htmlFor="rep-desc">
            <TextArea
              id="rep-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              maxLength={2000}
              placeholder="How did you receive it? (e.g. WhatsApp forward)"
            />
          </Field>

          {loading && <LoadingState label="Submitting anonymized report…" />}
          {error && <Alert tone="error">{error}</Alert>}

          <Button type="submit" disabled={loading} className="h-11 px-8">
            {loading ? 'Submitting…' : 'Submit anonymous report'}
          </Button>
        </form>
      </Card>
    </Container>
  );
}
