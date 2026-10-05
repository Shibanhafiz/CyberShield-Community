import axios from 'axios';

// In dev, Vite proxies /api -> backend (see vite.config.js).
// VITE_BACKEND_URL is only needed if calling the backend directly.
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export async function getHealth() {
  const res = await api.get('/health');
  return res.data;
}

/**
 * Human-readable message from an API failure. Backend errors use
 * { error, message } (Phase 7); `detail` is kept as a legacy fallback.
 * Never surfaces raw internals — only the server-provided message or a
 * generic fallback.
 */
export function apiErrorMessage(err, fallback = 'Something went wrong. Please try again.') {
  const data = err?.response?.data;
  if (typeof data?.message === 'string' && data.message) return data.message;
  if (typeof data?.detail === 'string' && data.detail) return data.detail;
  if (!err?.response) return 'Cannot reach the backend. Make sure it is running.';
  return fallback;
}

export async function analyzeMessage(text) {
  const res = await api.post('/analyze/message', { text });
  return res.data;
}

export async function analyzeUrl(url) {
  const res = await api.post('/analyze/url', { url });
  return res.data;
}

export async function submitReport(payload) {
  const res = await api.post('/reports', payload);
  return res.data;
}

export async function getCommunityStats() {
  const res = await api.get('/community/stats');
  return res.data;
}

export async function getCommunityTrends(granularity = 'day') {
  const res = await api.get('/community/trends', { params: { granularity } });
  return res.data;
}

export async function getCommunityCategories() {
  const res = await api.get('/community/categories');
  return res.data;
}

export async function getCommunityAreas() {
  const res = await api.get('/community/areas');
  return res.data;
}

export async function getTopics() {
  const res = await api.get('/learning/topics');
  return res.data;
}

export async function getTopic(slug) {
  const res = await api.get(`/learning/topics/${slug}`);
  return res.data;
}

export async function getScenarios() {
  const res = await api.get('/learning/scenarios');
  return res.data;
}

export async function getScenario(id) {
  const res = await api.get(`/learning/scenarios/${id}`);
  return res.data;
}

export async function answerScenario(id, selected) {
  const res = await api.post(`/learning/scenarios/${id}/answer`, { selected });
  return res.data;
}

export async function getQuizQuestions(quizType = 'quiz', count = 20) {
  const res = await api.get('/quiz/questions', { params: { quiz_type: quizType, count } });
  return res.data;
}

export async function submitQuizAttempt(sessionId, quizType, answers) {
  const res = await api.post('/quiz/attempt', {
    session_id: sessionId, quiz_type: quizType, answers,
  });
  return res.data;
}

export async function submitBefore(sessionId, answers) {
  const res = await api.post('/awareness/before', { session_id: sessionId, answers });
  return res.data;
}

export async function submitAfter(sessionId, answers) {
  const res = await api.post('/awareness/after', { session_id: sessionId, answers });
  return res.data;
}

export async function getAwarenessSession(sessionId) {
  const res = await api.get(`/awareness/session/${sessionId}`);
  return res.data;
}

export async function getImpactSummary() {
  const res = await api.get('/impact/summary');
  return res.data;
}

/** Anonymous session id persisted in localStorage (Phase 5: no accounts). */
export function getSessionId() {
  let sid = null;
  try {
    sid = localStorage.getItem('cybershield_session');
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem('cybershield_session', sid);
    }
  } catch {
    sid = '00000000-0000-4000-8000-000000000000';
  }
  return sid;
}

/* ---------- Admin auth (Phase 6, JWT in memory + localStorage) ---------- */

const ADMIN_TOKEN_KEY = 'cybershield_admin_token';

export function getAdminToken() {
  try {
    return localStorage.getItem(ADMIN_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAdminToken(token, profile) {
  try {
    if (token) {
      localStorage.setItem(ADMIN_TOKEN_KEY, token);
      localStorage.setItem('cybershield_admin_profile', JSON.stringify(profile || {}));
    } else {
      localStorage.removeItem(ADMIN_TOKEN_KEY);
      localStorage.removeItem('cybershield_admin_profile');
    }
  } catch { /* private mode: token held in memory only */ }
  setAdminToken._memory = token || null;
  if (profile !== undefined) setAdminToken._profile = profile || null;
}

export function getAdminProfile() {
  if (setAdminToken._profile !== undefined && setAdminToken._profile !== null) {
    return setAdminToken._profile;
  }
  try {
    const raw = localStorage.getItem('cybershield_admin_profile');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearAdminToken() {
  setAdminToken(null, null);
}

function adminHeaders() {
  const token = setAdminToken._memory || getAdminToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function adminLogin(email, password) {
  const res = await api.post('/admin/login', { email, password });
  return res.data;
}

export async function adminMe() {
  const res = await api.get('/admin/me', { headers: adminHeaders() });
  return res.data;
}

export async function adminOverview() {
  const res = await api.get('/admin/overview', { headers: adminHeaders() });
  return res.data;
}

export async function adminReports(params = {}) {
  const res = await api.get('/admin/reports', { headers: adminHeaders(), params });
  return res.data;
}

export async function adminReport(id) {
  const res = await api.get(`/admin/reports/${id}`, { headers: adminHeaders() });
  return res.data;
}

export async function adminUpdateReportStatus(id, status) {
  const res = await api.patch(`/admin/reports/${id}/status`, { status }, { headers: adminHeaders() });
  return res.data;
}

export async function adminAnalyticsSummary() {
  const res = await api.get('/admin/analytics/summary', { headers: adminHeaders() });
  return res.data;
}

export async function adminAwarenessSummary() {
  const res = await api.get('/admin/awareness/summary', { headers: adminHeaders() });
  return res.data;
}

export async function adminFeedback() {
  const res = await api.get('/admin/feedback', { headers: adminHeaders() });
  return res.data;
}

export async function adminFeedbackStats() {
  const res = await api.get('/admin/feedback/stats', { headers: adminHeaders() });
  return res.data;
}

export async function submitFeedback(payload) {
  const res = await api.post('/feedback', payload);
  return res.data;
}

export async function adminAudit(params = {}) {
  const res = await api.get('/admin/audit', { headers: adminHeaders(), params });
  return res.data;
}

export async function adminUsers() {
  const res = await api.get('/admin/users', { headers: adminHeaders() });
  return res.data;
}

export async function adminExport(name) {
  const res = await api.get(`/admin/export/${name}`, {
    headers: adminHeaders(),
    responseType: 'blob',
  });
  return res;
}

export default api;
