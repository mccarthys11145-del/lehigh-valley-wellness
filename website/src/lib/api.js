const RELATIVE_DEFAULT = '/api';
const LOCAL_DEFAULT = 'http://localhost:5001/api';

const isBrowser = typeof window !== 'undefined';
const hasDocument = typeof document !== 'undefined';

function normalizeBaseUrl(raw) {
  if (!raw) return '';

  const trimmed = raw.trim();
  if (!trimmed) return '';

  let normalizedValue = trimmed;

  if (!isAbsoluteUrl(normalizedValue) && !normalizedValue.startsWith('/')) {
    if (/[.:]/.test(normalizedValue)) {
      normalizedValue = `https://${normalizedValue}`;
    } else {
      normalizedValue = `/${normalizedValue}`;
    }
  }

  const withoutTrailingSlash = normalizedValue.replace(/\/+$/, '');

  if (/\/consultation-requests$/i.test(withoutTrailingSlash)) {
    // Treat fully qualified endpoints as-is so callers can point directly at
    // the consultation requests resource when needed.
    return withoutTrailingSlash;
  }

  if (/\/api(\/|$)/i.test(withoutTrailingSlash)) {
    return withoutTrailingSlash;
  }

  return `${withoutTrailingSlash}/api`;
}

function isAbsoluteUrl(value) {
  return /^https?:\/\//i.test(value);
}

function resolveConfiguredBaseUrl() {
  const sources = [];

  if (typeof import.meta !== 'undefined' && import.meta.env) {
    sources.push(import.meta.env.VITE_CRM_API_BASE_URL);
    sources.push(import.meta.env.VITE_CRM_API_URL);
  }

  if (isBrowser) {
    sources.push(window.__CRM_API_URL__);

    if (hasDocument) {
      const metaValue = document
        .querySelector('meta[name="crm-api-base"]')
        ?.getAttribute('content');
      sources.push(metaValue);
    }
  }

  for (const source of sources) {
    const normalized = normalizeBaseUrl(source);
    if (normalized) {
      return normalized;
    }
  }

  return '';
}

export function getCrmApiBaseUrl() {
  const configuredBase = resolveConfiguredBaseUrl();
  if (configuredBase) {
    return configuredBase;
  }

  if (isBrowser) {
    const hostname = window.location.hostname;
    if (/^(localhost|127\.0\.0\.1)$/i.test(hostname)) {
      return LOCAL_DEFAULT;
    }

    if (isAbsoluteUrl(window.location.origin)) {
      return normalizeBaseUrl(window.location.origin);
    }
  }

  return RELATIVE_DEFAULT;
}

export function buildCrmApiUrl(path = '') {
  const baseUrl = getCrmApiBaseUrl();
  const normalizedPath = path ? (path.startsWith('/') ? path : `/${path}`) : '';

  if (!baseUrl) {
    return normalizedPath || '';
  }

  const trimmedBase = baseUrl.replace(/\/+$/, '');

  if (!normalizedPath) {
    return trimmedBase;
  }

  const normalizedPathLower = normalizedPath.toLowerCase();
  if (trimmedBase.toLowerCase().endsWith(normalizedPathLower)) {
    return trimmedBase;
  }

  return `${trimmedBase}${normalizedPath}`;
}