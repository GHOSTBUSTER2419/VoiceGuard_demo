/**
 * VoiceGuard — API Service Layer
 *
 * REST API wrappers for all backend endpoints.
 * Base URL is proxied via Vite dev server.
 */

const BASE = '/api/v1';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API request failed');
  }
  return res.json();
}

// --- Sessions ---
export function createSession(data) {
  return request('/sessions', { method: 'POST', body: JSON.stringify(data) });
}

export function getSession(id) {
  return request(`/sessions/${id}`);
}

// --- Demo ---
export function triggerSimulation(data) {
  return request('/demo/simulate', { method: 'POST', body: JSON.stringify(data) });
}

export function getDemoStatus() {
  return request('/demo/status');
}

// --- Org Config ---
export function getOrgConfig(orgId = 'default') {
  return request(`/orgs/${orgId}/config`);
}

export function updateOrgConfig(orgId = 'default', data) {
  return request(`/orgs/${orgId}/config`, { method: 'PUT', body: JSON.stringify(data) });
}

// --- Alerts ---
export function getAlerts(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/alerts${qs ? `?${qs}` : ''}`);
}

export function submitFeedback(alertId, data) {
  return request(`/alerts/${alertId}/feedback`, { method: 'POST', body: JSON.stringify(data) });
}

// --- Voiceprints ---
export function enrollVoiceprint(data) {
  return request('/voiceprints', { method: 'POST', body: JSON.stringify(data) });
}

// --- Banking ---
export function checkTransaction(data) {
  return request('/banking/check', { method: 'POST', body: JSON.stringify(data) });
}

export function requestStepUp(data) {
  return request('/banking/step-up', { method: 'POST', body: JSON.stringify(data) });
}

export function verifyTransaction(data) {
  return request('/banking/verify', { method: 'POST', body: JSON.stringify(data) });
}

export function blockTransaction(data) {
  return request('/banking/block', { method: 'POST', body: JSON.stringify(data) });
}
