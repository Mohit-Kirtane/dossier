async function unwrap(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export function getDbSchema() {
  return fetch("/api/database-chat/schema").then((res) => unwrap(res));
}

export function sendDbChatMessage(question) {
  return fetch("/api/database-chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  }).then((res) => unwrap(res));
}
