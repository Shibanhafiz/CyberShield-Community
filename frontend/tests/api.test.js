import { describe, expect, test } from 'vitest';
import { apiErrorMessage, getSessionId } from '../src/api';

describe('apiErrorMessage', () => {
  test('prefers the Phase 7 {error,message} shape', () => {
    const err = { response: { status: 400, data: { error: 'invalid_request', message: 'Bad input.' } } };
    expect(apiErrorMessage(err)).toBe('Bad input.');
  });

  test('falls back to legacy detail', () => {
    const err = { response: { status: 400, data: { detail: 'Old shape.' } } };
    expect(apiErrorMessage(err)).toBe('Old shape.');
  });

  test('offline requests get a connectivity message', () => {
    expect(apiErrorMessage({}, 'fb')).toMatch(/backend/i);
  });

  test('unknown shapes get the caller fallback', () => {
    expect(apiErrorMessage({ response: { status: 500, data: {} } }, 'Try later.')).toBe('Try later.');
  });

  test('never returns non-string internals', () => {
    const out = apiErrorMessage({ response: { status: 500, data: { error: 42 } } }, 'fb');
    expect(typeof out).toBe('string');
  });
});

describe('getSessionId', () => {
  test('creates and persists a stable anonymous id', () => {
    const first = getSessionId();
    const second = getSessionId();
    expect(first).toBe(second);
    expect(first).toMatch(/^[0-9a-f-]{36}$/i);
  });

  test('stores only an anonymous id, never credentials', () => {
    getSessionId();
    const keys = [];
    for (let i = 0; i < window.localStorage.length; i += 1) keys.push(window.localStorage.key(i));
    expect(keys).not.toContain('cybershield_admin_token');
    expect(window.localStorage.getItem('cybershield_admin_token')).toBeNull();
  });
});
