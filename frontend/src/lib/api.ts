import type { ChatResponse, DocumentOut } from "./types";

async function unwrap<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export function listDocuments(): Promise<DocumentOut[]> {
  return fetch("/api/documents").then((res) => unwrap(res));
}

export function uploadDocument(file: File): Promise<DocumentOut> {
  const form = new FormData();
  form.append("file", file);
  return fetch("/api/documents/upload", { method: "POST", body: form }).then((res) =>
    unwrap(res),
  );
}

export function sendChatMessage(
  question: string,
  sessionId: string | null,
): Promise<ChatResponse> {
  return fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  }).then((res) => unwrap(res));
}
