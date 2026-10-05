import { useState } from 'react';
import { Link2, Mail, MessageSquareText } from 'lucide-react';
import AnalysisResult from '../components/AnalysisResult';
import LoadingState from '../components/LoadingState';
import UrlAnalysisResult from '../components/UrlAnalysisResult';
import { Alert, Button, Container, Field, TextArea, TextInput } from '../components/ui';
import { analyzeMessage, analyzeUrl, apiErrorMessage } from '../api';

const tabs = [
  { id: 'message', label: 'Message', icon: MessageSquareText, live: true },
  { id: 'url', label: 'URL', icon: Link2, live: true },
  { id: 'email', label: 'Email', icon: Mail, live: false, note: 'Email checks are not available yet — paste the text under the Message tab for a text-signal assessment.' },
];

function errorText(err) {
  const status = err?.response?.status;
  if (status === 400 || status === 422) return apiErrorMessage(err, 'We couldn’t analyze this input. Please check it and try again.');
  if (status === 429) return apiErrorMessage(err, 'Too many analysis requests. Please wait a little and try again.');
  if (status === 503) return apiErrorMessage(err, 'The analysis service is temporarily unavailable. Please try again later.');
  return apiErrorMessage(err, 'We couldn’t analyze this right now. Please try again.');
}

export default function Analyze({ initialTab = 'message' }) {
  const [tab, setTab] = useState(initialTab === 'url' ? 'url' : 'message');
  const [value, setValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [resultKind, setResultKind] = useState(null);

  const active = tabs.find((t) => t.id === tab);
  const isUrl = tab === 'url';

  async function handleAnalyze() {
    if (!value.trim()) {
      setError(isUrl ? 'Please paste a URL first.' : 'Please paste a message first.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = isUrl
        ? await analyzeUrl(value.trim())
        : await analyzeMessage(value.trim());
      setResult(data);
      setResultKind(isUrl ? 'url' : 'message');
    } catch (err) {
      setError(errorText(err));
    } finally {
      setLoading(false);
    }
  }

  function handleTab(id) {
    setTab(id);
    setError('');
    setResult(null);
    setResultKind(null);
  }

  function handleReset() {
    setValue('');
    setResult(null);
    setResultKind(null);
  }

  return (
    <Container narrow>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Analyzer</p>
      <h1 className="mt-1.5 text-2xl font-bold tracking-tight text-ink md:text-[28px]">
        {isUrl ? 'Check a suspicious link' : 'Check a suspicious message'}
      </h1>
      <p className="mt-2 max-w-xl text-[15px] leading-relaxed text-ink-2">
        {isUrl
          ? 'We inspect the link’s structure for common deception patterns. The link is never visited.'
          : 'We check the text against common scam indicators and explain what we find.'}
      </p>

      <div className="mt-5 flex gap-1 rounded-xl border border-line bg-surface p-1.5" role="tablist" aria-label="What to check">
        {tabs.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => handleTab(t.id)}
            className={`flex h-10 flex-1 items-center justify-center gap-2 rounded-lg text-sm font-semibold transition-colors ${
              tab === t.id ? 'bg-brand-tint text-brand-dark' : 'text-ink-2 hover:bg-surface-2'
            }`}
          >
            <t.icon size={16} aria-hidden />
            {t.label}
          </button>
        ))}
      </div>

      {!result && (
        <div className="mt-5">
          {isUrl ? (
            <Field label="Paste a URL" htmlFor="analyze-input">
              <TextInput
                id="analyze-input"
                type="text"
                inputMode="url"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                maxLength={2048}
                placeholder="https://example.com/login"
                autoComplete="off"
              />
            </Field>
          ) : (
            <Field
              label={tab === 'email' ? 'Email text' : 'Paste the message'}
              htmlFor="analyze-input"
              hint={tab === 'email' ? active.note : undefined}
            >
              <TextArea
                id="analyze-input"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                rows={7}
                maxLength={5000}
                className="min-h-[180px]"
                placeholder="Paste an SMS, WhatsApp message, email, or other suspicious text..."
              />
            </Field>
          )}

          <p className="mt-2 text-[13px] text-muted">
            Don’t enter passwords, OTPs, PINs, CVVs, or other sensitive information.
          </p>

          <div className="mt-4">
            {active.live ? (
              <Button onClick={handleAnalyze} disabled={loading} className="h-12 w-full px-6 text-[15px] sm:w-auto">
                {loading ? 'Analyzing…' : isUrl ? 'Analyze URL' : 'Analyze message'}
              </Button>
            ) : (
              <Alert tone="info">{active.note}</Alert>
            )}
          </div>

          {loading && (
            <div className="mt-4">
              <LoadingState label={isUrl ? 'Inspecting URL structure…' : 'Checking message indicators…'} />
            </div>
          )}
          {error && (
            <div className="mt-4">
              <Alert tone="error">{error}</Alert>
            </div>
          )}
        </div>
      )}

      {result && resultKind === 'message' && <AnalysisResult result={result} sourceText={value} onReset={handleReset} />}
      {result && resultKind === 'url' && <UrlAnalysisResult result={result} onReset={handleReset} />}
    </Container>
  );
}
