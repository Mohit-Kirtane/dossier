import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import type { Message } from "../lib/types";
import { MessageBubble } from "./MessageBubble";

interface ChatPanelProps {
  messages: Message[];
  onSend: (question: string) => void;
  disabled?: boolean;
}

export function ChatPanel({ messages, onSend, disabled }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
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
          <div className="mt-24 text-center text-sm text-slate-500">
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
        className="mx-auto flex w-full max-w-3xl items-center gap-3 border-t border-slate-800 px-8 py-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your documents..."
          className="flex-1 rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="flex items-center gap-2 rounded-lg bg-indigo-500 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-600 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Send className="h-4 w-4" />
          Send
        </button>
      </form>
    </main>
  );
}
