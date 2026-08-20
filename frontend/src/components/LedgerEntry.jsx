import { Loader2 } from "lucide-react";

export function LedgerEntry({ message }) {
  if (message.role === "user") {
    return (
      <div className="ledger-row flex items-baseline justify-end gap-2 text-right">
        <span className="font-mono text-[10px] font-medium tracking-[0.18em] text-ochre">ASK</span>
        <p className="font-body text-sm text-paper">{message.content}</p>
      </div>
    );
  }

  if (message.error) {
    return (
      <div className="ledger-row flex items-baseline gap-2">
        <span className="font-mono text-[10px] font-medium tracking-[0.18em] text-ink-soft">
          ERROR
        </span>
        <p className="font-body text-sm text-rose-300/90">{message.content}</p>
      </div>
    );
  }

  const uniqueSources = message.sources ? [...new Set(message.sources.map((s) => s.source))] : [];

  return (
    <div className="ledger-row rounded-lg border border-ink/10 bg-paper p-5 shadow-[0_20px_40px_-24px_rgba(0,0,0,0.6)]">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink/50">
          ANSWER
        </span>
        {!message.pending && (
          <span
            className={`rounded-full px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide ${
              uniqueSources.length > 0
                ? "border border-ochre-deep/40 bg-ochre/15 text-ochre-deep"
                : "border border-ink/15 text-ink/40"
            }`}
          >
            {uniqueSources.length > 0 ? "CITED" : "NO MATCH"}
          </span>
        )}
      </div>

      {message.pending ? (
        <span className="mt-3 flex items-center gap-2 font-body text-sm text-ink/60">
          <Loader2 className="h-4 w-4 animate-spin text-ochre-deep" />
          Filing an answer…
        </span>
      ) : (
        <>
          <p className="mt-3 font-body text-sm leading-relaxed whitespace-pre-wrap text-ink">
            {message.content}
          </p>
          {uniqueSources.length > 0 && (
            <p className="mt-3 border-t border-ink/10 pt-2 font-mono text-[11px] tracking-wide text-ink/50">
              [source: {uniqueSources.join(", ")}]
            </p>
          )}
        </>
      )}
    </div>
  );
}
