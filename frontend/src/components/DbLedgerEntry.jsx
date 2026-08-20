import { ReasoningTrace } from "./ReasoningTrace.jsx";
import { useTypewriter } from "../lib/useTypewriter.js";

const STEPS = ["WRITING SQL", "VALIDATING QUERY", "RUNNING QUERY", "SUMMARIZING"];
const PREVIEW_ROWS = 8;

function ResultsTable({ columns, rows }) {
  const preview = rows.slice(0, PREVIEW_ROWS);
  return (
    <div className="mt-3 overflow-x-auto rounded-md border border-ink/10">
      <table className="w-full text-left font-body text-xs">
        <thead>
          <tr className="border-b border-ink/10 bg-ink/[0.04]">
            {columns.map((col) => (
              <th
                key={col}
                className="whitespace-nowrap px-3 py-1.5 font-mono text-[10px] font-medium tracking-wide text-ink/50"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {preview.map((row, i) => (
            <tr key={i} className="border-b border-ink/5 last:border-0">
              {columns.map((col) => (
                <td key={col} className="whitespace-nowrap px-3 py-1.5 text-ink">
                  {String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > PREVIEW_ROWS && (
        <p className="border-t border-ink/10 bg-ink/[0.04] px-3 py-1 font-mono text-[10px] tracking-wide text-ink/50">
          +{rows.length - PREVIEW_ROWS} more row{rows.length - PREVIEW_ROWS === 1 ? "" : "s"}
        </p>
      )}
    </div>
  );
}

export function DbLedgerEntry({ message }) {
  const { shown, done } = useTypewriter(message.pending ? "" : message.content);

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

  const hasRows = (message.rows?.length ?? 0) > 0;
  const badge = !message.sql ? "REFUSED" : hasRows ? `${message.rows.length} ROWS` : "NO MATCH";

  return (
    <div className="ledger-row rounded-lg border border-ink/10 bg-paper p-5 shadow-[0_20px_40px_-24px_rgba(0,0,0,0.6)]">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink/50">
          ANSWER
        </span>
        {!message.pending && (
          <span
            className={`rounded-full px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide ${
              hasRows
                ? "border border-ochre-deep/40 bg-ochre/15 text-ochre-deep"
                : "border border-ink/15 text-ink/40"
            }`}
          >
            {badge}
          </span>
        )}
      </div>

      {message.pending ? (
        <div className="mt-3 text-ink/60">
          <ReasoningTrace steps={STEPS} />
        </div>
      ) : (
        <>
          <p className="mt-3 font-body text-sm leading-relaxed whitespace-pre-wrap text-ink">
            {shown}
            {!done && <span className="typing-caret h-4 align-middle" />}
          </p>
          {done && message.sql && (
            <pre className="mt-3 overflow-x-auto rounded-md border border-ink/10 bg-ink/[0.04] px-3 py-2 font-mono text-[11px] leading-relaxed text-ink/70">
              {message.sql}
            </pre>
          )}
          {done && hasRows && <ResultsTable columns={message.columns} rows={message.rows} />}
        </>
      )}
    </div>
  );
}
