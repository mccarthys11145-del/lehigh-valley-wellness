export function getCrmApiBaseUrl() {
  const rawBase = (import.meta.env.VITE_CRM_API_URL || '').trim();
  const fallbackBase = import.meta.env.DEV
    ? 'http://localhost:5001'
    : (typeof window !== 'undefined' ? window.location.origin : '');

  const base = (rawBase || fallbackBase || 'http://localhost:5001').replace(/\/+$/, '');

  if (/\/api(\/|$)/.test(base)) {
    return base;
  }

  return `${base}/api`;
}

export function buildCrmApiUrl(path = '') {
  const baseUrl = getCrmApiBaseUrl();
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}
