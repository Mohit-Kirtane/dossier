import { Loader2 } from "lucide-react";
import type { Message } from "../lib/types";

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const uniqueSources = message.sources
    ? [...new Set(message.sources.map((s) => s.source))]
    : [];

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-slate-800 text-slate-100"
            : "border border-slate-800 bg-slate-900/60 text-slate-200"
        }`}
      >
        {message.pending ? (
          <span className="flex items-center gap-2 text-slate-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            Thinking…
          </span>
        ) : (
          <>
            {message.content}
            {uniqueSources.length > 0 && (
              <p className="mt-2 border-t border-slate-800 pt-2 text-xs text-slate-500">
                Sources: {uniqueSources.join(", ")}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
