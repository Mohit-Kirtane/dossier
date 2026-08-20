import { Logo } from "../brand/Logo.jsx";
import { GithubMark } from "../brand/GithubMark.jsx";

export function SiteFooter() {
  return (
    <footer className="mx-auto w-full max-w-6xl px-6 pb-12 sm:px-10">
      <div className="flex flex-col items-start justify-between gap-4 border-t border-rule pt-6 sm:flex-row sm:items-center">
        <div className="flex items-center gap-2 text-ink-soft">
          <Logo className="h-4 w-4" />
          <span className="font-mono text-[11px] tracking-wide">
            ENTERPRISE KNOWLEDGE COPILOT — MIT LICENSED
          </span>
        </div>
        <a
          href="https://github.com/Mohit-Kirtane/enterprise-knowledge-copilot"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 font-body text-sm text-ink-soft transition hover:text-paper"
        >
          <GithubMark className="h-4 w-4" />
          github.com/Mohit-Kirtane/enterprise-knowledge-copilot
        </a>
      </div>
    </footer>
  );
}
