async function unwrap(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export function registerUser(email, password, name) {
  return fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  }).then((res) => unwrap(res));
}

export function loginUser(email, password) {
  return fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }).then((res) => unwrap(res));
}

export function logoutUser() {
  return fetch("/api/auth/logout", { method: "POST" }).then((res) => unwrap(res));
}

export function fetchCurrentUser() {
  return fetch("/api/auth/me").then((res) => (res.ok ? res.json() : null));
}

export const googleLoginUrl = "/api/auth/google/login";

export function getMyActivity() {
  return fetch("/api/activity/me").then((res) => unwrap(res));
}

export function getAllActivity() {
  return fetch("/api/admin/activity").then((res) => unwrap(res));
}
