import { useCallback, useEffect, useState } from "react";
import { PolicySidebar } from "../components/PolicySidebar.jsx";
import { PolicyChatPanel } from "../components/PolicyChatPanel.jsx";
import {
  getPersonas,
  getPolicyDocuments,
  sendPolicyChatMessage,
  uploadPolicyDocument,
} from "../lib/policyChatApi.js";

export default function PolicyChatPage() {
  const [personas, setPersonas] = useState([]);
  const [activePersonaId, setActivePersonaId] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    getPersonas().then((list) => {
      setPersonas(list);
      if (list.length > 0) setActivePersonaId(list[0].id);
    });
  }, []);

  const refreshDocuments = useCallback(async (personaId) => {
    if (!personaId) return;
    setDocuments(await getPolicyDocuments(personaId));
  }, []);

  useEffect(() => {
    refreshDocuments(activePersonaId).catch(() => undefined);
  }, [activePersonaId, refreshDocuments]);

  function handleSwitchPersona(personaId) {
    setActivePersonaId(personaId);
    setMessages([]);
    setSidebarOpen(false);
  }

  async function handleUpload(file, allowedRoles) {
    await uploadPolicyDocument(file, allowedRoles);
    await refreshDocuments(activePersonaId);
  }

  async function handleSend(question) {
    const userMessage = { id: crypto.randomUUID(), role: "user", content: question };
    const pendingId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: pendingId, role: "assistant", content: "", pending: true },
    ]);
    setSending(true);
    try {
      const res = await sendPolicyChatMessage(question, activePersonaId);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                id: pendingId,
                role: "assistant",
                content: res.answer,
                sources: res.sources,
                restricted: res.restricted,
              }
            : m,
        ),
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                id: pendingId,
                role: "assistant",
                content: err instanceof Error ? err.message : "Something went wrong.",
                error: true,
              }
            : m,
        ),
      );
    } finally {
      setSending(false);
    }
  }

  function handleReset() {
    setMessages([]);
  }

  const activePersona = personas.find((p) => p.id === activePersonaId) ?? null;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-ink">
      <PolicySidebar
        personas={personas}
        activePersonaId={activePersonaId}
        onSwitchPersona={handleSwitchPersona}
        documents={documents}
        onUpload={handleUpload}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <PolicyChatPanel
        activePersona={activePersona}
        messages={messages}
        onSend={handleSend}
        onReset={handleReset}
        disabled={sending}
        onOpenSidebar={() => setSidebarOpen(true)}
      />
    </div>
  );
}
