import { Link } from "react-router-dom";
import { ArrowRight, Database, FileText, Receipt, ShieldCheck } from "lucide-react";

const WORKFLOWS = [
  {
    code: "FILE—01",
    status: "LIVE",
    path: "/app",
    title: "Document intelligence",
    description: "Upload PDFs, DOCX, or text. Ask questions, get answers grounded in cited passages.",
    icon: FileText,
  },
  {
    code: "FILE—02",
    status: "LIVE",
    path: "/app/database-chat",
    title: "Database chat",
    description: "Query structured databases in plain language instead of writing SQL by hand.",
    icon: Database,
  },
  {
    code: "FILE—03",
    status: "QUEUED",
    title: "RBAC policy retrieval",
    description: "Retrieval scoped to what a role is permitted to see, enforced at query time.",
    icon: ShieldCheck,
  },
  {
    code: "FILE—04",
    status: "QUEUED",
    title: "Invoice intelligence",
    description: "Extract structured line items and answer questions over invoice documents.",
    icon: Receipt,
  },
];

function WorkflowCard({ workflow }) {
  const Icon = workflow.icon;
  const isLive = workflow.status === "LIVE";

  const content = (
    <div
      className={`flex h-full flex-col rounded-lg border p-5 transition ${
        isLive
          ? "border-ochre-deep/50 bg-ink-raised hover:border-ochre"
          : "border-rule bg-ink-raised/50"
      }`}
    >
      <div className="flex items-start justify-between">
        <span className="font-mono text-[11px] tracking-[0.1em] text-ink-soft">{workflow.code}</span>
        <span
          className={`rounded-full px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide ${
            isLive
              ? "border border-ochre-deep/40 bg-ochre/15 text-ochre"
              : "border border-rule text-ink-soft"
          }`}
        >
          {workflow.status}
        </span>
      </div>

      <Icon className={`mt-6 h-5 w-5 ${isLive ? "text-ochre" : "text-ink-soft"}`} />

      <h3 className="mt-4 font-display text-lg font-medium text-paper">{workflow.title}</h3>
      <p className="mt-2 flex-1 font-body text-sm leading-relaxed text-ink-soft">
        {workflow.description}
      </p>

      {isLive && (
        <span className="mt-5 flex items-center gap-1.5 font-body text-sm font-medium text-ochre">
          Try it <ArrowRight className="h-3.5 w-3.5" />
        </span>
      )}
    </div>
  );

  return isLive ? (
    <Link to={workflow.path} className="block h-full">
      {content}
    </Link>
  ) : (
    <div className="h-full">{content}</div>
  );
}

export function WorkflowIndex() {
  return (
    <section id="workflows" className="mx-auto w-full max-w-6xl px-6 py-20 sm:px-10">
      <div className="mb-10 flex items-end justify-between gap-6 border-b border-rule pb-5">
        <div>
          <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ochre">
            THE INDEX
          </p>
          <h2 className="mt-2 font-display text-2xl font-medium text-paper sm:text-3xl">
            Four modules, one platform
          </h2>
        </div>
        <p className="hidden max-w-xs text-right font-body text-sm text-ink-soft sm:block">
          Each workflow is an independent LangGraph pipeline behind the same FastAPI service.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {WORKFLOWS.map((workflow) => (
          <WorkflowCard key={workflow.code} workflow={workflow} />
        ))}
      </div>
    </section>
  );
}
