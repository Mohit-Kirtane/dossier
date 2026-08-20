import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { FileText, Loader2, UploadCloud } from "lucide-react";
import { Logo } from "./brand/Logo.jsx";
import { GithubMark } from "./brand/GithubMark.jsx";
import { ModuleTabs } from "./ModuleTabs.jsx";
import { UserMenu } from "./UserMenu.jsx";
import { checkUploadSize, MAX_UPLOAD_SIZE_MB } from "../lib/uploadLimits.js";

export function Sidebar({ documents, onUpload, selectedDocumentId, onSelectDocument }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
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
      await onUpload(file);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col gap-5 border-r border-rule bg-ink-raised/60 p-5">
      <Link to="/" className="flex items-center gap-2.5 text-paper transition hover:text-ochre">
        <Logo className="h-6 w-6 shrink-0" />
        <div>
          <h1 className="font-display text-[15px] font-medium leading-tight">
            Dossier
          </h1>
          <p className="font-mono text-[10px] tracking-wide text-ink-soft">FILE—01 · DOCUMENT INTELLIGENCE</p>
        </div>
      </Link>

      <ModuleTabs />

      <label
        className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg border border-dashed border-rule px-4 py-6 text-center font-body text-sm text-ink-soft transition hover:border-ochre hover:text-paper ${
          uploading ? "pointer-events-none opacity-60" : ""
        }`}
      >
        {uploading ? (
          <Loader2 className="h-5 w-5 animate-spin text-ochre" />
        ) : (
          <UploadCloud className="h-5 w-5" />
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

      {error && <p className="font-body text-xs text-rose-400">{error}</p>}

      <div className="flex-1 space-y-2 overflow-y-auto">
        <div className="flex items-center justify-between">
          <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
            THE INDEX
          </p>
          {selectedDocumentId && (
            <button
              type="button"
              onClick={() => onSelectDocument?.(null)}
              className="font-mono text-[10px] tracking-wide text-ink-soft transition hover:text-ochre"
            >
              CLEAR SCOPE
            </button>
          )}
        </div>
        {documents.length === 0 && (
          <p className="font-body text-xs text-ink-soft/70">Nothing indexed yet.</p>
        )}
        {documents.length > 0 && (
          <p className="font-body text-[11px] leading-relaxed text-ink-soft/70">
            Select a file to chat about that document only.
          </p>
        )}
        {documents.map((doc, i) => {
          const active = doc.id === selectedDocumentId;
          return (
            <button
              key={doc.id}
              type="button"
              onClick={() => onSelectDocument?.(active ? null : doc.id)}
              className={`w-full rounded-lg border p-3 text-left transition ${
                active
                  ? "border-ochre-deep/50 bg-ochre/10"
                  : "border-rule bg-ink-raised/50 hover:border-ochre-deep/50"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-mono text-[10px] tracking-[0.1em] text-ink-soft">
                  DOC—{String(i + 1).padStart(2, "0")}
                </span>
                <span
                  className={`rounded-full border px-2 py-0.5 font-mono text-[9px] font-medium tracking-wide ${
                    active
                      ? "border-ochre bg-ochre text-ink"
                      : "border-ochre-deep/40 bg-ochre/15 text-ochre-deep"
                  }`}
                >
                  {active ? "SCOPED" : "INDEXED"}
                </span>
              </div>
              <div className="mt-2 flex items-start gap-2">
                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-ink-soft" />
                <div className="min-w-0">
                  <p className={`truncate font-body text-sm font-medium ${active ? "text-ochre" : "text-paper"}`}>
                    {doc.filename}
                  </p>
                  <p className="font-mono text-[11px] text-ink-soft">
                    {doc.chunk_count} {doc.chunk_count === 1 ? "chunk" : "chunks"}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
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
