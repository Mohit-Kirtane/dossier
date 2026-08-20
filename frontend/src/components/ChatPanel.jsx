import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { MessageBubble } from "./MessageBubble.jsx";

export function ChatPanel({ messages, onSend, disabled }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || disabled) return;
    onSend(question);
    setInput("");
  }

  return (
    <main className="flex h-full flex-1 flex-col">
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {messages.length === 0 ? (
          <div className="mt-24 text-center font-body text-sm text-ink-soft">
            Upload a document, then ask a question about it.
          </div>
        ) : (
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="mx-auto flex w-full max-w-3xl items-center gap-3 border-t border-rule px-8 py-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your documents..."
          className="flex-1 rounded-lg border border-rule bg-ink-raised px-4 py-3 font-body text-sm text-paper outline-none placeholder:text-ink-soft focus:border-ochre"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="flex items-center gap-2 rounded-lg bg-ochre px-5 py-3 font-body text-sm font-medium text-ink transition hover:bg-ochre-deep hover:text-paper disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Send className="h-4 w-4" />
          Send
        </button>
      </form>
    </main>
  );
}
