import { useEffect, useRef, useState } from "react";
import { RotateCcw, Send } from "lucide-react";
import { DbLedgerEntry } from "./DbLedgerEntry.jsx";

const EXAMPLES = [
  "Which customers have overdue invoices, and how much do they owe?",
  "Which sales rep owns the most active contract value?",
  "What's the average time to close a support ticket, by priority?",
];

export function DbChatPanel({ messages, onSend, onReset, disabled }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function submit(question) {
    if (!question.trim() || disabled) return;
    onSend(question.trim());
    setInput("");
  }

  return (
    <main className="flex h-full flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-rule px-8 py-4">
        <p className="font-mono text-[11px] tracking-[0.18em] text-ink-soft">
          WORKSPACE <span className="text-ink-soft/40">/</span> DATABASE CHAT
        </p>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={onReset}
            className="flex items-center gap-1.5 font-mono text-[11px] tracking-wide text-ink-soft transition hover:text-ochre"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            NEW SESSION
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-8 py-8">
        {messages.length === 0 ? (
          <div className="mx-auto mt-16 max-w-md rounded-lg border border-dashed border-rule px-6 py-10 text-center">
            <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
              NO QUERIES YET
            </p>
            <p className="mt-3 font-body text-sm leading-relaxed text-ink-soft">
              Ask a question in plain language about customers, contracts, invoices,
              payments, or support tickets — no SQL required.
            </p>
            <div className="mt-5 flex flex-col gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  type="button"
                  onClick={() => submit(ex)}
                  className="rounded-md border border-rule px-3 py-2 text-left font-body text-xs text-ink-soft transition hover:border-ochre-deep/50 hover:text-paper"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="mx-auto flex max-w-2xl flex-col gap-5">
            {messages.map((m) => (
              <DbLedgerEntry key={m.id} message={m} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit(input);
        }}
        className="mx-auto flex w-full max-w-2xl items-center gap-3 border-t border-rule px-8 py-5"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about customers, contracts, invoices, or support tickets..."
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
