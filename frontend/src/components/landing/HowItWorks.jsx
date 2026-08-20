function Pipeline({ title, description, steps }) {
  return (
    <div>
      <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ochre">{title}</p>
      <p className="mt-2 max-w-md font-body text-sm text-ink-soft">{description}</p>

      <div className="mt-6 flex flex-col gap-0 sm:flex-row sm:items-stretch sm:gap-0">
        {steps.map((step, i) => (
          <div key={step.label} className="flex flex-1 items-stretch sm:items-center">
            <div
              className={`w-full rounded-md border px-4 py-3 sm:w-auto ${
                step.key
                  ? "border-ochre-deep/50 bg-ochre/10"
                  : "border-rule bg-ink-raised"
              }`}
            >
              <p
                className={`font-mono text-xs font-medium tracking-wide ${
                  step.key ? "text-ochre" : "text-paper"
                }`}
              >
                {step.label}
              </p>
              <p className="mt-1 font-body text-xs text-ink-soft">{step.caption}</p>
            </div>
            {i < steps.length - 1 && (
              <div className="flex h-6 items-center justify-center px-2 text-ink-soft sm:h-auto sm:px-3">
                <span aria-hidden className="font-mono text-sm">
                  →
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export function HowItWorks() {
  return (
    <section id="architecture" className="mx-auto w-full max-w-6xl px-6 py-20 sm:px-10">
      <div className="mb-10 border-b border-rule pb-5">
        <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ochre">
          UNDER THE HOOD
        </p>
        <h2 className="mt-2 font-display text-2xl font-medium text-paper sm:text-3xl">
          Two pipelines, no wasted calls
        </h2>
      </div>

      <div className="space-y-12">
        <Pipeline
          title="INGESTION"
          description="Runs once per document, entirely offline — no LLM calls."
          steps={[
            { label: "UPLOAD", caption: "PDF, DOCX, or text" },
            { label: "CHUNK", caption: "RecursiveCharacterTextSplitter" },
            { label: "EMBED", caption: "MiniLM-L6-v2, local CPU" },
            { label: "INDEX", caption: "FAISS, persisted to disk" },
          ]}
        />
        <Pipeline
          title="RETRIEVAL"
          description="A LangGraph state machine that only calls the LLM when there's something worth answering with."
          steps={[
            { label: "ASK", caption: "Natural-language question" },
            { label: "RETRIEVE", caption: "FAISS similarity search" },
            { label: "FILTER", caption: "Below threshold → decline, 0 calls", key: true },
            { label: "GENERATE", caption: "Gemini, grounded in excerpts" },
            { label: "CITE", caption: "Answer + source filename" },
          ]}
        />
      </div>
    </section>
  );
}
