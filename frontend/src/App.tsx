import { useCallback, useEffect, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatPanel } from "./components/ChatPanel";
import { listDocuments, sendChatMessage, uploadDocument } from "./lib/api";
import type { DocumentOut, Message } from "./lib/types";

export default function App() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  const refreshDocuments = useCallback(async () => {
    setDocuments(await listDocuments());
  }, []);

  useEffect(() => {
    refreshDocuments().catch(() => undefined);
  }, [refreshDocuments]);

  async function handleUpload(file: File) {
    await uploadDocument(file);
    await refreshDocuments();
  }

  async function handleSend(question: string) {
    const userMessage: Message = { id: crypto.randomUUID(), role: "user", content: question };
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
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar documents={documents} onUpload={handleUpload} />
      <ChatPanel messages={messages} onSend={handleSend} disabled={sending} />
    </div>
  );
}
