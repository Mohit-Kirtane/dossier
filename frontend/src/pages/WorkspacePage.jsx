import { useCallback, useEffect, useState } from "react";
import { Sidebar } from "../components/Sidebar.jsx";
import { ChatPanel } from "../components/ChatPanel.jsx";
import { listDocuments, sendChatMessage, uploadDocument } from "../lib/api.js";

export default function WorkspacePage() {
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [sending, setSending] = useState(false);

  const refreshDocuments = useCallback(async () => {
    setDocuments(await listDocuments());
  }, []);

  useEffect(() => {
    refreshDocuments().catch(() => undefined);
  }, [refreshDocuments]);

  async function handleUpload(file) {
    await uploadDocument(file);
    await refreshDocuments();
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
      const res = await sendChatMessage(question, sessionId);
      setSessionId(res.session_id);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? { id: pendingId, role: "assistant", content: res.answer, sources: res.sources }
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
              }
            : m,
        ),
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-ink">
      <Sidebar documents={documents} onUpload={handleUpload} />
      <ChatPanel messages={messages} onSend={handleSend} disabled={sending} />
    </div>
  );
}
