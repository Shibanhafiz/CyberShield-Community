import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// crypto.randomUUID is used for anonymous session ids; ensure it exists.
if (typeof globalThis.crypto === 'undefined' || !globalThis.crypto.randomUUID) {
  const { webcrypto } = await import('node:crypto').catch(() => ({}));
  if (webcrypto && typeof globalThis.crypto === 'undefined') {
    globalThis.crypto = webcrypto;
  }
}

// jsdom lacks these; charts/layout code may touch them.
if (typeof window.matchMedia === 'undefined') {
  window.matchMedia = () => ({
    matches: false,
    addListener() {},
    removeListener() {},
    addEventListener() {},
    removeEventListener() {},
    dispatchEvent() { return false; },
  });
}
if (typeof window.ResizeObserver === 'undefined') {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  window.localStorage.clear();
});
