const INGEST = [
  { label: "UPLOAD", value: "sample.txt" },
  { label: "CHUNK", value: "1 segment · 1,000 chars" },
  { label: "EMBED", value: "MiniLM-L6-v2, local" },
  { label: "INDEX", value: "FAISS — persisted" },
];

const QUERY = [
  { label: "ASK", value: '"How many vacation days do employees get?"' },
  { label: "RETRIEVE", value: "top k=4, cosine similarity" },
  { label: "SCORE", value: "0.85 — above threshold" },
  { label: "GENERATE", value: "gemini-3.6-flash" },
];

function LedgerGroup({ title, rows, baseDelay, animate }) {
  return (
    <div>
      <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink/50">{title}</p>
      <dl className="mt-2 space-y-1.5">
        {rows.map((row, i) => (
          <div
            key={row.label}
            className={`flex items-baseline justify-between gap-4 font-mono text-[13px] ${animate ? "ledger-row" : ""}`}
            style={animate ? { animationDelay: `${baseDelay + i * 0.12}s` } : undefined}
          >
            <dt className="shrink-0 text-ink/60">{row.label}</dt>
            <dd className="truncate text-right text-ink">{row.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function LedgerTrace({ animate = false }) {
  return (
    <div className="w-full max-w-md rounded-lg border border-ink/10 bg-paper p-6 shadow-[0_30px_60px_-20px_rgba(0,0,0,0.5)]">
      <div className="mb-4 flex items-center justify-between">
        <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink/50">LEDGER TRACE</p>
        <span className="rounded-full border border-ochre-deep/40 bg-ochre/15 px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-ochre-deep">
          LIVE
        </span>
      </div>

      <LedgerGroup title="INGEST" rows={INGEST} baseDelay={0} animate={animate} />

      <hr className="my-4 border-ink/10" />

      <LedgerGroup title="QUERY" rows={QUERY} baseDelay={0.6} animate={animate} />

      <div
        className={`mt-4 rounded-md border border-ink/10 bg-ink/[0.04] p-3 ${animate ? "ledger-row" : ""}`}
        style={animate ? { animationDelay: "1.4s" } : undefined}
      >
        <p className="font-body text-[13px] leading-snug text-ink">
          "Full-time employees accrue 18 days of paid time off per year, and up to 10 unused days
          carry over."
        </p>
        <p className="mt-1.5 font-mono text-[11px] text-ink/50">[source: sample.txt]</p>
      </div>
    </div>
  );
}
