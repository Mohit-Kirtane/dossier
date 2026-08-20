import { useRef, useState } from "react";
import { FileText, Loader2, Sparkles, UploadCloud } from "lucide-react";
import type { DocumentOut } from "../lib/types";

interface SidebarProps {
  documents: DocumentOut[];
  onUpload: (file: File) => Promise<void>;
}

export function Sidebar({ documents, onUpload }: SidebarProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File | undefined) {
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
    <aside className="flex h-full w-80 shrink-0 flex-col gap-5 border-r border-slate-800 bg-slate-950/60 p-5">
      <div className="flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-indigo-400" />
        <div>
          <h1 className="text-sm font-semibold leading-tight text-slate-100">
            Enterprise Knowledge Copilot
          </h1>
          <p className="text-xs text-slate-500">Document intelligence · RAG over your files</p>
        </div>
      </div>

      <label
        className={`flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-dashed border-slate-700 px-4 py-6 text-center text-sm text-slate-400 transition hover:border-indigo-500 hover:text-slate-200 ${
          uploading ? "pointer-events-none opacity-60" : ""
        }`}
      >
        {uploading ? (
          <Loader2 className="h-5 w-5 animate-spin text-indigo-400" />
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

      {error && <p className="text-xs text-rose-400">{error}</p>}

      <div className="flex-1 space-y-2 overflow-y-auto">
        {documents.length === 0 && (
          <p className="text-xs text-slate-600">No documents uploaded yet.</p>
        )}
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="flex items-start gap-2 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2"
          >
            <FileText className="mt-0.5 h-4 w-4 shrink-0 text-slate-500" />
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-slate-200">{doc.filename}</p>
              <p className="text-xs text-slate-500">
                {doc.chunk_count} {doc.chunk_count === 1 ? "chunk" : "chunks"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
