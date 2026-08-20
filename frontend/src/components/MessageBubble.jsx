import { Loader2 } from "lucide-react";

export function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const uniqueSources = message.sources
    ? [...new Set(message.sources.map((s) => s.source))]
    : [];

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 font-body text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-ink-raised text-paper"
            : "border border-rule bg-ink-raised/40 text-paper"
        }`}
      >
        {message.pending ? (
          <span className="flex items-center gap-2 text-ink-soft">
            <Loader2 className="h-4 w-4 animate-spin text-ochre" />
            Thinking…
          </span>
        ) : (
          <>
            {message.content}
            {uniqueSources.length > 0 && (
              <p className="mt-2 border-t border-rule pt-2 font-mono text-[11px] tracking-wide text-ink-soft">
                [source: {uniqueSources.join(", ")}]
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
