import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { FileText, Loader2, UploadCloud } from "lucide-react";
import { Logo } from "./brand/Logo.jsx";
import { GithubMark } from "./brand/GithubMark.jsx";

export function Sidebar({ documents, onUpload }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
    setError(null);
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
            Enterprise Knowledge Copilot
          </h1>
          <p className="font-mono text-[10px] tracking-wide text-ink-soft">FILE—01 · DOCUMENT INTELLIGENCE</p>
        </div>
      </Link>

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
        <span>{uploading ? "Uploading…" : "Click to upload a PDF, DOCX, or TXT"}</span>
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
        <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ink-soft">
          THE INDEX
        </p>
        {documents.length === 0 && (
          <p className="font-body text-xs text-ink-soft/70">Nothing indexed yet.</p>
        )}
        {documents.map((doc, i) => (
          <div
            key={doc.id}
            className="rounded-lg border border-rule bg-ink-raised/50 p-3 transition hover:border-ochre-deep/50"
          >
            <div className="flex items-start justify-between gap-2">
              <span className="font-mono text-[10px] tracking-[0.1em] text-ink-soft">
                DOC—{String(i + 1).padStart(2, "0")}
              </span>
              <span className="rounded-full border border-ochre-deep/40 bg-ochre/15 px-2 py-0.5 font-mono text-[9px] font-medium tracking-wide text-ochre-deep">
                INDEXED
              </span>
            </div>
            <div className="mt-2 flex items-start gap-2">
              <FileText className="mt-0.5 h-4 w-4 shrink-0 text-ink-soft" />
              <div className="min-w-0">
                <p className="truncate font-body text-sm font-medium text-paper">{doc.filename}</p>
                <p className="font-mono text-[11px] text-ink-soft">
                  {doc.chunk_count} {doc.chunk_count === 1 ? "chunk" : "chunks"}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <a
        href="https://github.com/Mohit-Kirtane/enterprise-knowledge-copilot"
        target="_blank"
        rel="noreferrer"
        className="flex items-center gap-1.5 border-t border-rule pt-4 font-mono text-[11px] tracking-wide text-ink-soft transition hover:text-paper"
      >
        <GithubMark className="h-3.5 w-3.5" />
        SOURCE
      </a>
    </aside>
  );
}
