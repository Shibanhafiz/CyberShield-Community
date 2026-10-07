import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import LoadingState from '../../components/LoadingState';
import PageMeta from '../../components/PageMeta';
import { Alert, Button, Card, Container, Field, TextInput } from '../../components/ui';
import { adminLogin, apiErrorMessage, setAdminToken } from '../../api';

export default function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError('Enter your admin email and password.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await adminLogin(email.trim(), password);
      setAdminToken(data.access_token, { email: data.email, role: data.role });
      navigate('/admin', { replace: true });
    } catch (err) {
      const status = err?.response?.status;
      setError(apiErrorMessage(
        err,
        status === 429
          ? 'Too many login attempts. Please try again later.'
          : 'Login failed. Please check your details and try again.',
      ));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Container narrow>
      <PageMeta
        title="Admin Login"
        description="Restricted sign-in for authorized CyberShield Community reviewers."
      />
      <div className="mx-auto max-w-md">
        <Card>
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-tint text-brand-dark" aria-hidden>
            <ShieldCheck size={20} />
          </span>
          <h1 className="mt-3 text-xl font-bold text-ink">Admin login</h1>
          <p className="mt-1 text-[13px] leading-relaxed text-muted">
            Restricted to authorized project reviewers. Sessions expire after 60 minutes.
          </p>
          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <Field label="Email" htmlFor="admin-email">
              <TextInput
                id="admin-email"
                type="email"
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@example.com"
              />
            </Field>
            <Field label="Password" htmlFor="admin-password">
              <TextInput
                id="admin-password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </Field>
            {loading && <LoadingState label="Signing in…" />}
            {error && <Alert tone="error">{error}</Alert>}
            <Button type="submit" disabled={loading} className="h-11 w-full">
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
        </Card>
      </div>
    </Container>
  );
}
