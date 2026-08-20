import { useEffect, useRef, useState } from "react";
import { Menu, RotateCcw, Send } from "lucide-react";
import { LedgerEntry } from "./LedgerEntry.jsx";

export function ChatPanel({ messages, onSend, onReset, disabled, scopedDocument, onOpenSidebar }) {
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
      <div className="flex items-center justify-between gap-3 border-b border-rule px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={onOpenSidebar}
            aria-label="Open sidebar"
            className="shrink-0 text-ink-soft transition hover:text-paper lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>
          <p className="truncate font-mono text-[11px] tracking-[0.18em] text-ink-soft">
            WORKSPACE <span className="text-ink-soft/40">/</span> DOCUMENT INTELLIGENCE
            {scopedDocument && (
              <>
                {" "}
                <span className="text-ink-soft/40">/</span>{" "}
                <span className="text-ochre">SCOPED TO {scopedDocument.toUpperCase()}</span>
              </>
            )}
          </p>
        </div>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={onReset}
            className="flex shrink-0 items-center gap-1.5 font-mono text-[11px] tracking-wide text-ink-soft transition hover:text-ochre"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">NEW SESSION</span>
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        {messages.length === 0 ? (
          <div className="mx-auto mt-16 max-w-sm rounded-lg border border-dashed border-rule px-6 py-10 text-center">
            <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
              NO ENTRIES YET
            </p>
            <p className="mt-3 font-body text-sm leading-relaxed text-ink-soft">
              {scopedDocument
                ? `Ask anything about ${scopedDocument} — every answer here comes filed with its source.`
                : "Upload a document in the sidebar, then select it to ask a question — every answer here comes filed with its source."}
            </p>
          </div>
        ) : (
          <div className="mx-auto flex max-w-2xl flex-col gap-5">
            {messages.map((m) => (
              <LedgerEntry key={m.id} message={m} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="mx-auto flex w-full max-w-2xl items-center gap-3 border-t border-rule px-4 py-4 sm:px-6 sm:py-5 lg:px-8"
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
