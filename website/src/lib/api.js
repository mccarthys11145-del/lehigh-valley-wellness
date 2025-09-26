const RELATIVE_DEFAULT = '/api';
const LOCAL_DEFAULT = 'http://localhost:5001/api';

const isBrowser = typeof window !== 'undefined';
const hasDocument = typeof document !== 'undefined';

export function isAbsoluteUrl(value) {
  return typeof value === 'string' && /^https?:\/\//i.test(value);
}

function normalizeBaseUrl(raw) {
  if (!raw) return '';

  const trimmed = `${raw}`.trim();
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
    return withoutTrailingSlash;
  }

  if (/\/api(\/|$)/i.test(withoutTrailingSlash)) {
    return withoutTrailingSlash;
  }

  return `${withoutTrailingSlash}/api`;
}

function normalizePath(path) {
  if (!path) return '';

  const trimmed = `${path}`.trim();
  if (!trimmed) return '';

  if (isAbsoluteUrl(trimmed)) {
    return trimmed;
  }

  return trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
}

function toCandidateArray(value) {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.flatMap(toCandidateArray);
  }

  if (typeof value === 'string') {
    return value
      .split(/[,\s]+/)
      .map((segment) => segment.trim())
      .filter(Boolean);
  }

  return [];
}

function resolveConfiguredBaseUrls() {
  const sources = [];

  if (typeof import.meta !== 'undefined' && import.meta.env) {
    const env = import.meta.env;
    sources.push(env.VITE_CRM_API_BASE_URLS);
    sources.push(env.VITE_CRM_API_URLS);
    sources.push(env.VITE_CRM_API_BASE_URL);
    sources.push(env.VITE_CRM_API_URL);
  }

  if (isBrowser) {
    if (Array.isArray(window.__CRM_API_URLS__)) {
      sources.push(window.__CRM_API_URLS__);
    } else {
      sources.push(window.__CRM_API_URLS__);
    }

    sources.push(window.__CRM_API_URL__);

    if (hasDocument) {
      const metaTags = document.querySelectorAll('meta[name="crm-api-base"], meta[name="crm-api-bases"]');
      metaTags.forEach((meta) => {
        sources.push(meta.getAttribute('content'));
      });
    }
  }

  const seen = new Set();
  const normalized = [];

  for (const candidate of sources.flatMap(toCandidateArray)) {
    const normalizedCandidate = normalizeBaseUrl(candidate);
    if (normalizedCandidate && !seen.has(normalizedCandidate)) {
      seen.add(normalizedCandidate);
      normalized.push(normalizedCandidate);
    }
  }

  return normalized;
}

export function getCrmApiBaseUrls() {
  const configured = resolveConfiguredBaseUrls();
  if (configured.length > 0) {
    return configured;
  }

  const fallbacks = [];

  if (isBrowser) {
    const hostname = window.location.hostname;
    if (/^(localhost|127\.0\.0\.1)$/i.test(hostname)) {
      fallbacks.push(LOCAL_DEFAULT);
    }

    if (isAbsoluteUrl(window.location.origin)) {
      const normalizedOrigin = normalizeBaseUrl(window.location.origin);
      if (normalizedOrigin) {
        fallbacks.push(normalizedOrigin);
      }
    }
  } else {
    fallbacks.push(LOCAL_DEFAULT);
  }

  fallbacks.push(RELATIVE_DEFAULT);

  const seen = new Set();
  const deduped = [];

  for (const candidate of fallbacks) {
    const normalizedCandidate = normalizeBaseUrl(candidate);
    if (normalizedCandidate && !seen.has(normalizedCandidate)) {
      seen.add(normalizedCandidate);
      deduped.push(normalizedCandidate);
    }
  }

  return deduped;
}

export function getCrmApiBaseUrl() {
  const [first] = getCrmApiBaseUrls();
  return first || '';
}

function generatePathVariants(path) {
  const normalized = normalizePath(path);

  if (!normalized) {
    return [''];
  }

  if (isAbsoluteUrl(normalized)) {
    return [normalized];
  }

  const variants = [normalized];

  if (/^\/consultation-requests\b/i.test(normalized)) {
    variants.push(`/patients${normalized}`);
  }

  return Array.from(new Set(variants));
}

function joinBaseAndPath(base, path) {
  if (!base) {
    return path;
  }

  const trimmedBase = base.replace(/\/+$/, '');
  if (!path) {
    return trimmedBase;
  }

  const lowerBase = trimmedBase.toLowerCase();
  const lowerPath = path.toLowerCase();

  if (lowerBase.endsWith(lowerPath)) {
    return trimmedBase;
  }

  if (lowerBase.endsWith('/patients') && lowerPath.startsWith('/patients')) {
    return `${trimmedBase}${path.slice('/patients'.length)}`;
  }

  return `${trimmedBase}${path}`;
}

export function buildCrmApiUrl(path = '', base = undefined) {
  if (isAbsoluteUrl(path)) {
    return path;
  }

  const targetBase = typeof base === 'string' && base ? normalizeBaseUrl(base) : getCrmApiBaseUrl();
  const normalizedPath = normalizePath(path);

  if (!targetBase) {
    return normalizedPath || '';
  }

  const fullUrl = joinBaseAndPath(targetBase, normalizedPath);
  const lowerPath = normalizedPath.toLowerCase();

  if (lowerPath && fullUrl.toLowerCase().endsWith(lowerPath)) {
    return fullUrl;
  }

  return fullUrl;
}

function expandBaseVariants(base) {
  if (!base) {
    return [];
  }

  const trimmed = base.replace(/\/+$/, '');
  const variants = [trimmed];

  if (/\/patients$/i.test(trimmed)) {
    variants.push(trimmed.replace(/\/patients$/i, ''));
  }

  if (/\/consultation-requests$/i.test(trimmed)) {
    variants.push(trimmed.replace(/\/consultation-requests$/i, ''));
  }

  return Array.from(new Set(variants.filter(Boolean)));
}

export function buildCrmApiUrlCandidates(path = '') {
  const variants = generatePathVariants(path);
  const bases = getCrmApiBaseUrls();
  const seen = new Set();
  const candidates = [];

  if (!bases.length) {
    for (const variant of variants) {
      if (variant && !seen.has(variant)) {
        seen.add(variant);
        candidates.push(variant);
      }
    }
    return candidates;
  }

  for (const base of bases) {
    const normalizedBase = normalizeBaseUrl(base);
    if (!normalizedBase) continue;

    for (const baseVariant of expandBaseVariants(normalizedBase)) {
      for (const variant of variants) {
        if (isAbsoluteUrl(variant)) {
          if (!seen.has(variant)) {
            seen.add(variant);
            candidates.push(variant);
          }
          continue;
        }

        const candidate = joinBaseAndPath(baseVariant, variant);
        if (!seen.has(candidate)) {
          seen.add(candidate);
          candidates.push(candidate);
        }
      }
    }
  }

  return candidates;
}

async function safeReadResponseBody(response) {
  try {
    return await response.clone().text();
  } catch (error) {
    return '';
  }
}

async function parseJsonResponse(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch (error) {
    const parsingError = new Error('Failed to parse CRM response as JSON');
    parsingError.cause = error;
    throw parsingError;
  }
}

export async function fetchCrm(path, init = {}, { parser = parseJsonResponse } = {}) {
  const urls = buildCrmApiUrlCandidates(path);
  if (!urls.length) {
    const error = new Error('No CRM API endpoints are configured.');
    throw error;
  }

  const attempts = [];
  let lastError;

  for (const url of urls) {
    try {
      const response = await fetch(url, init);
      if (!response.ok) {
        const body = await safeReadResponseBody(response);
        attempts.push({ url, status: response.status, body });
        lastError = new Error(`HTTP ${response.status}`);
        continue;
      }

      if (!parser) {
        return { url, status: response.status, data: undefined };
      }

      const data = await parser(response);
      return { url, status: response.status, data };
    } catch (error) {
      attempts.push({ url, error });
      lastError = error;
    }
  }

  const error = new Error('All CRM API endpoints failed');
  error.attempts = attempts;
  if (lastError) {
    error.cause = lastError;
  }

  throw error;
}

export async function fetchCrmJson(path, init = {}) {
  return fetchCrm(path, init, { parser: parseJsonResponse });
}

export async function submitConsultationRequest(payload) {
  const requestInit = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  };

  return fetchCrmJson('/consultation-requests', requestInit);
}