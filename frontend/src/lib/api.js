async function unwrap(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export function listDocuments() {
  return fetch("/api/documents").then((res) => unwrap(res));
}

export function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);
  return fetch("/api/documents/upload", { method: "POST", body: form }).then((res) =>
    unwrap(res),
  );
}

export function sendChatMessage(question, sessionId) {
  return fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  }).then((res) => unwrap(res));
}
