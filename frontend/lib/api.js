// Small fetch wrapper around the Django backend.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TOKEN_KEY = "hda_access_token";
const REFRESH_KEY = "hda_refresh_token";

export function getToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setTokens({ access, refresh }) {
  if (typeof window === "undefined") return;
  if (access) window.localStorage.setItem(TOKEN_KEY, access);
  if (refresh) window.localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

export function isLoggedIn() {
  return !!getToken();
}

async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message = data.detail || data.error || JSON.stringify(data);
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export async function register({ username, email, password }) {
  const data = await request("/api/auth/register/", { method: "POST", body: { username, email, password } });
  setTokens(data);
  return data;
}

export async function login({ username, password }) {
  const data = await request("/api/auth/login/", { method: "POST", body: { username, password } });
  setTokens(data);
  return data;
}

export function logout() {
  clearTokens();
}

export async function me() {
  return request("/api/auth/me/", { auth: true });
}

export async function getHealth() {
  return request("/api/health/");
}

export async function getSymptoms() {
  return request("/api/symptoms/");
}

export async function getSamples() {
  return request("/api/samples/");
}

export async function diagnose(patient) {
  return request("/api/diagnose/", { method: "POST", body: patient, auth: true });
}

export async function getHistory() {
  return request("/api/history/", { auth: true });
}
