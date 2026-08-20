import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Logo } from "../components/brand/Logo.jsx";
import { ModuleTabs } from "../components/ModuleTabs.jsx";
import { getAllActivity, getMyActivity } from "../lib/authApi.js";

const EVENT_LABELS = {
  login: "LOGIN",
  register: "REGISTER",
  question_asked: "QUESTION",
  document_uploaded: "UPLOAD",
};

const WORKFLOW_LABELS = {
  document_intelligence: "Document Intel",
  database_chat: "Database Chat",
  policy_retrieval: "Policy Retrieval",
};

function ActivityTable({ rows, showUser }) {
  if (rows.length === 0) {
    return <p className="font-body text-sm text-ink-soft">No activity yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-rule">
      <table className="w-full text-left font-body text-sm">
        <thead>
          <tr className="border-b border-rule bg-ink-raised/50">
            <th className="whitespace-nowrap px-4 py-2.5 font-mono text-[10px] font-medium tracking-wide text-ink-soft">
              WHEN
            </th>
            {showUser && (
              <th className="whitespace-nowrap px-4 py-2.5 font-mono text-[10px] font-medium tracking-wide text-ink-soft">
                USER
              </th>
            )}
            <th className="whitespace-nowrap px-4 py-2.5 font-mono text-[10px] font-medium tracking-wide text-ink-soft">
              EVENT
            </th>
            <th className="whitespace-nowrap px-4 py-2.5 font-mono text-[10px] font-medium tracking-wide text-ink-soft">
              WORKFLOW
            </th>
            <th className="px-4 py-2.5 font-mono text-[10px] font-medium tracking-wide text-ink-soft">
              DETAIL
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} className="border-b border-rule/50 last:border-0 hover:bg-ink-raised/30">
              <td className="whitespace-nowrap px-4 py-2.5 font-mono text-xs text-ink-soft">
                {new Date(row.created_at).toLocaleString()}
              </td>
              {showUser && (
                <td className="whitespace-nowrap px-4 py-2.5 text-paper">
                  {row.user_name}
                  <span className="ml-1.5 text-ink-soft">{row.user_email}</span>
                </td>
              )}
              <td className="whitespace-nowrap px-4 py-2.5">
                <span className="rounded-full border border-ochre-deep/40 bg-ochre/15 px-2 py-0.5 font-mono text-[10px] font-medium tracking-wide text-ochre-deep">
                  {EVENT_LABELS[row.event_type] ?? row.event_type.toUpperCase()}
                </span>
              </td>
              <td className="whitespace-nowrap px-4 py-2.5 text-ink-soft">
                {WORKFLOW_LABELS[row.workflow] ?? "—"}
              </td>
              <td className="max-w-md truncate px-4 py-2.5 text-paper">{row.detail ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ActivityPage() {
  const [scope, setScope] = useState("all");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const fetcher = scope === "all" ? getAllActivity : getMyActivity;
    fetcher()
      .then(setRows)
      .finally(() => setLoading(false));
  }, [scope]);

  return (
    <div className="min-h-screen bg-ink">
      <header className="flex flex-col gap-4 border-b border-rule px-6 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-10">
        <Link to="/" className="flex items-center gap-2.5 text-paper transition hover:text-ochre">
          <Logo className="h-6 w-6" />
          <span className="font-mono text-[12px] font-medium tracking-[0.12em]">
            DOSSIER
          </span>
        </Link>
        <div className="overflow-x-auto">
          <ModuleTabs />
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl px-6 py-10 sm:px-10">
        <div className="mb-8 flex flex-col gap-4 border-b border-rule pb-5 sm:flex-row sm:items-end sm:justify-between sm:gap-6">
          <div>
            <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ochre">
              THE LEDGER
            </p>
            <h1 className="mt-2 font-display text-2xl font-medium text-paper sm:text-3xl">
              Activity
            </h1>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setScope("all")}
              className={`rounded-md border px-3 py-1.5 font-mono text-[11px] tracking-wide transition ${
                scope === "all"
                  ? "border-ochre-deep/50 bg-ochre/15 text-ochre-deep"
                  : "border-rule text-ink-soft hover:text-paper"
              }`}
            >
              ALL USERS
            </button>
            <button
              type="button"
              onClick={() => setScope("me")}
              className={`rounded-md border px-3 py-1.5 font-mono text-[11px] tracking-wide transition ${
                scope === "me"
                  ? "border-ochre-deep/50 bg-ochre/15 text-ochre-deep"
                  : "border-rule text-ink-soft hover:text-paper"
              }`}
            >
              MY ACTIVITY
            </button>
          </div>
        </div>

        {loading ? (
          <p className="font-mono text-[11px] tracking-wide text-ink-soft">LOADING…</p>
        ) : (
          <ActivityTable rows={rows} showUser={scope === "all"} />
        )}
      </main>
    </div>
  );
}
