import { Link } from "react-router-dom";
import { Table2 } from "lucide-react";
import { Logo } from "./brand/Logo.jsx";
import { GithubMark } from "./brand/GithubMark.jsx";
import { ModuleTabs } from "./ModuleTabs.jsx";
import { UserMenu } from "./UserMenu.jsx";

export function DbSchemaSidebar({ tables }) {
  return (
    <aside className="flex h-full w-80 shrink-0 flex-col gap-5 border-r border-rule bg-ink-raised/60 p-5">
      <Link to="/" className="flex items-center gap-2.5 text-paper transition hover:text-ochre">
        <Logo className="h-6 w-6 shrink-0" />
        <div>
          <h1 className="font-display text-[15px] font-medium leading-tight">
            Dossier
          </h1>
          <p className="font-mono text-[10px] tracking-wide text-ink-soft">FILE—02 · DATABASE CHAT</p>
        </div>
      </Link>

      <ModuleTabs />

      <div className="flex-1 space-y-2 overflow-y-auto">
        <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
          THE SCHEMA
        </p>
        {tables.length === 0 && (
          <p className="font-body text-xs text-ink-soft/70">Loading schema…</p>
        )}
        {tables.map((t) => (
          <div
            key={t.table}
            className="rounded-lg border border-rule bg-ink-raised/50 p-3 transition hover:border-ochre-deep/50"
          >
            <div className="flex items-start justify-between gap-2">
              <span className="flex items-center gap-1.5 font-body text-sm font-medium text-paper">
                <Table2 className="h-3.5 w-3.5 shrink-0 text-ink-soft" />
                {t.table.replace(/^demo_/, "")}
              </span>
              <span className="rounded-full border border-rule px-2 py-0.5 font-mono text-[9px] tracking-wide text-ink-soft">
                {t.columns.length} COLS
              </span>
            </div>
            <p className="mt-2 truncate font-mono text-[10px] tracking-wide text-ink-soft">
              {t.columns.map((c) => c.name).join(", ")}
            </p>
          </div>
        ))}
      </div>

      <a
        href="https://github.com/Mohit-Kirtane/dossier"
        target="_blank"
        rel="noreferrer"
        className="flex items-center gap-1.5 border-t border-rule pt-4 font-mono text-[11px] tracking-wide text-ink-soft transition hover:text-paper"
      >
        <GithubMark className="h-3.5 w-3.5" />
        SOURCE
      </a>

      <UserMenu />
    </aside>
  );
}
