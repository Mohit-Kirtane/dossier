import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Lock, Loader2, ShieldCheck, UploadCloud } from "lucide-react";
import { Logo } from "./brand/Logo.jsx";
import { GithubMark } from "./brand/GithubMark.jsx";
import { ModuleTabs } from "./ModuleTabs.jsx";
import { UserMenu } from "./UserMenu.jsx";
import { checkUploadSize, MAX_UPLOAD_SIZE_MB } from "../lib/uploadLimits.js";

const ROLE_LABELS = {
  employee: "Employee",
  manager: "Manager",
  hr: "HR",
  executive: "Executive",
};

export function PolicySidebar({ personas, activePersonaId, onSwitchPersona, documents, onUpload }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedRoles, setSelectedRoles] = useState(["employee"]);
  const inputRef = useRef(null);

  function toggleRole(role) {
    setSelectedRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role],
    );
  }

  async function handleFile(file) {
    if (!file) return;
    if (selectedRoles.length === 0) {
      setError("Select at least one role first");
      return;
    }
    setError(null);
    try {
      checkUploadSize(file);
    } catch (err) {
      setError(err.message);
      if (inputRef.current) inputRef.current.value = "";
      return;
    }
    setUploading(true);
    try {
      await onUpload(file, selectedRoles);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col gap-5 overflow-y-auto border-r border-rule bg-ink-raised/60 p-5">
      <Link to="/" className="flex items-center gap-2.5 text-paper transition hover:text-ochre">
        <Logo className="h-6 w-6 shrink-0" />
        <div>
          <h1 className="font-display text-[15px] font-medium leading-tight">
            Dossier
          </h1>
          <p className="font-mono text-[10px] tracking-wide text-ink-soft">FILE—03 · RBAC POLICY RETRIEVAL</p>
        </div>
      </Link>

      <ModuleTabs />

      <div>
        <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
          VIEWING AS
        </p>
        <div className="mt-2 flex flex-col gap-1.5">
          {personas.map((p) => {
            const active = p.id === activePersonaId;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => onSwitchPersona(p.id)}
                className={`flex items-center justify-between rounded-lg border px-3 py-2 text-left transition ${
                  active
                    ? "border-ochre-deep/50 bg-ochre/10"
                    : "border-rule bg-ink-raised/50 hover:border-ochre-deep/30"
                }`}
              >
                <div>
                  <p className={`font-body text-sm font-medium ${active ? "text-ochre" : "text-paper"}`}>
                    {p.name}
                  </p>
                  <p className="font-mono text-[10px] text-ink-soft">{p.title}</p>
                </div>
                {active && <ShieldCheck className="h-4 w-4 shrink-0 text-ochre" />}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <p className="mb-2 font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
          UPLOAD A POLICY
        </p>
        <div className="mb-2 flex flex-wrap gap-1.5">
          {Object.entries(ROLE_LABELS).map(([role, label]) => (
            <button
              key={role}
              type="button"
              onClick={() => toggleRole(role)}
              className={`rounded-full border px-2.5 py-1 font-mono text-[10px] tracking-wide transition ${
                selectedRoles.includes(role)
                  ? "border-ochre-deep/40 bg-ochre/15 text-ochre-deep"
                  : "border-rule text-ink-soft"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <label
          className={`flex cursor-pointer flex-col items-center gap-1.5 rounded-lg border border-dashed border-rule px-4 py-4 text-center font-body text-xs text-ink-soft transition hover:border-ochre hover:text-paper ${
            uploading ? "pointer-events-none opacity-60" : ""
          }`}
        >
          {uploading ? (
            <Loader2 className="h-4 w-4 animate-spin text-ochre" />
          ) : (
            <UploadCloud className="h-4 w-4" />
          )}
          <span>{uploading ? "Uploading…" : `Click to upload a PDF, DOCX, or TXT (max ${MAX_UPLOAD_SIZE_MB} MB)`}</span>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </label>
        {error && <p className="mt-1.5 font-body text-xs text-rose-400">{error}</p>}
      </div>

      <div className="flex-1 space-y-2">
        <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
          THE REGISTRY
        </p>
        {documents.length === 0 && (
          <p className="font-body text-xs text-ink-soft/70">No policies loaded yet.</p>
        )}
        {documents.map((doc) => (
          <div
            key={doc.id}
            className={`rounded-lg border p-3 ${
              doc.visible ? "border-rule bg-ink-raised/50" : "border-rule/60 bg-ink-raised/20"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <span
                className={`truncate font-body text-sm font-medium ${
                  doc.visible ? "text-paper" : "text-ink-soft/60 line-through decoration-ink-soft/30"
                }`}
              >
                {doc.filename}
              </span>
              {doc.visible ? (
                <ShieldCheck className="h-4 w-4 shrink-0 text-ochre-deep" />
              ) : (
                <Lock className="h-4 w-4 shrink-0 text-ink-soft/50" />
              )}
            </div>
            <p className="mt-1 font-mono text-[10px] tracking-wide text-ink-soft">
              {doc.allowed_roles.map((r) => ROLE_LABELS[r] ?? r).join(", ")}
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
