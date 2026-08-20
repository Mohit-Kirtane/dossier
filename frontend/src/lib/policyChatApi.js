async function unwrap(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export function getPersonas() {
  return fetch("/api/policy-chat/personas").then((res) => unwrap(res));
}

export function getPolicyDocuments(personaId) {
  return fetch(`/api/policy-chat/documents?persona_id=${encodeURIComponent(personaId)}`).then((res) =>
    unwrap(res),
  );
}

export function uploadPolicyDocument(file, allowedRoles) {
  const form = new FormData();
  form.append("file", file);
  allowedRoles.forEach((role) => form.append("allowed_roles", role));
  return fetch("/api/policy-chat/upload", { method: "POST", body: form }).then((res) => unwrap(res));
}

export function sendPolicyChatMessage(question, personaId) {
  return fetch("/api/policy-chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, persona_id: personaId }),
  }).then((res) => unwrap(res));
}
