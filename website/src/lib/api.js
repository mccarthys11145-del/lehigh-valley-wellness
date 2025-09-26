const LOCAL_DEFAULT = 'http://localhost:5001';

const isBrowser = typeof window !== 'undefined';
const hasDocument = typeof document !== 'undefined';

function normalizeBaseUrl(value) {
  if (!value) return '';

  const trimmed = value.trim();
  if (!trimmed) return '';

  const withoutTrailingSlash = trimmed.replace(/\/+$/, '');

  if (/\/api(\/|$)/.test(withoutTrailingSlash)) {
    return withoutTrailingSlash;
  }

  return `${withoutTrailingSlash}/api`;
}

function shouldSkipUrl(candidate) {
  if (!candidate) return true;

  if (!isBrowser) {
    return false;
  }

  if (!candidate.startsWith('http://')) {
    return false;
  }

  const isLocalHostTarget = /http:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(candidate);
  if (isLocalHostTarget) {
    const isLocalPage = /^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname);
    if (isLocalPage) {
      return false;
    }
  }

  // Avoid mixed-content requests when the site is served over HTTPS.
  return window.location.protocol === 'https:';
}

function unique(values) {
  const seen = new Set();
  const result = [];

  for (const value of values) {
    if (!value || seen.has(value)) continue;
    seen.add(value);
    result.push(value);
  }

  return result;
}

export function getCrmApiBaseUrlCandidates() {
  const candidates = [];

  const addCandidate = (value) => {
    const normalized = normalizeBaseUrl(value);
    if (!normalized || shouldSkipUrl(normalized)) {
      return;
    }
    candidates.push(normalized);
  };

  if (typeof import.meta !== 'undefined' && import.meta.env) {
    addCandidate(import.meta.env.VITE_CRM_API_URL);
  }

  if (isBrowser) {
    if (window.__CRM_API_URL__) {
      addCandidate(window.__CRM_API_URL__);
    }

    const meta = hasDocument
      ? document.querySelector('meta[name="crm-api-base"]')?.getAttribute('content')
      : null;
    if (meta) {
      addCandidate(meta);
    }
  }

  if (isBrowser) {
    addCandidate(window.location.origin);
  }

  const isLocalEnv = (typeof import.meta !== 'undefined' && import.meta.env?.DEV) || (isBrowser && /^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname));
  if (isLocalEnv) {
    addCandidate(LOCAL_DEFAULT);
  }

  addCandidate(LOCAL_DEFAULT);

  return unique(candidates);
}

export function getCrmApiBaseUrl() {
  const [firstCandidate = ''] = getCrmApiBaseUrlCandidates();
  return firstCandidate;
}

export function buildCrmApiUrl(path = '') {
  const baseUrl = getCrmApiBaseUrl();
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}

