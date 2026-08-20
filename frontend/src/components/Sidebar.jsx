import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { FileText, Loader2, UploadCloud } from "lucide-react";
import { Logo } from "./brand/Logo.jsx";

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
        {documents.length === 0 && (
          <p className="font-body text-xs text-ink-soft/70">No documents uploaded yet.</p>
        )}
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="flex items-start gap-2 rounded-lg border border-rule bg-ink/40 px-3 py-2"
          >
            <FileText className="mt-0.5 h-4 w-4 shrink-0 text-ink-soft" />
            <div className="min-w-0">
              <p className="truncate font-body text-sm font-medium text-paper">{doc.filename}</p>
              <p className="font-mono text-[11px] text-ink-soft">
                {doc.chunk_count} {doc.chunk_count === 1 ? "chunk" : "chunks"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
