import { useEffect, useState } from "react";
import { DbSchemaSidebar } from "../components/DbSchemaSidebar.jsx";
import { DbChatPanel } from "../components/DbChatPanel.jsx";
import { getDbSchema, sendDbChatMessage } from "../lib/dbChatApi.js";

export default function DatabaseChatPage() {
  const [tables, setTables] = useState([]);
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    getDbSchema()
      .then(setTables)
      .catch(() => undefined);
  }, []);

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
      const res = await sendDbChatMessage(question);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                id: pendingId,
                role: "assistant",
                content: res.answer,
                sql: res.sql,
                columns: res.columns,
                rows: res.rows,
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

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-ink">
      <DbSchemaSidebar tables={tables} open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <DbChatPanel
        messages={messages}
        onSend={handleSend}
        onReset={handleReset}
        disabled={sending}
        onOpenSidebar={() => setSidebarOpen(true)}
      />
    </div>
  );
}
