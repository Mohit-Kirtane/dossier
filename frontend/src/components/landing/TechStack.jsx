const STACK = [
  "REACT",
  "JAVASCRIPT",
  "FASTAPI",
  "LANGGRAPH",
  "LANGCHAIN",
  "FAISS",
  "GEMINI",
  "POSTGRESQL",
];

export function TechStack() {
  return (
    <section className="mx-auto w-full max-w-6xl px-6 py-14 sm:px-10">
      <div className="flex flex-wrap items-center gap-3 border-t border-rule pt-10">
        <span className="mr-2 font-mono text-[11px] tracking-[0.18em] text-ink-soft">STAMPED WITH</span>
        {STACK.map((name) => (
          <span
            key={name}
            className="rounded border border-rule px-2.5 py-1 font-mono text-[11px] tracking-wide text-ink-soft"
          >
            {name}
          </span>
        ))}
      </div>
    </section>
  );
}
