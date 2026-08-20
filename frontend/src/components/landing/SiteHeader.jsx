import { Link } from "react-router-dom";
import { Logo } from "../brand/Logo.jsx";
import { GithubMark } from "../brand/GithubMark.jsx";

export function SiteHeader() {
  return (
    <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6 sm:px-10">
      <Link to="/" className="flex items-center gap-2.5 text-paper">
        <Logo className="h-6 w-6 text-paper" />
        <span className="font-mono text-[13px] font-medium tracking-[0.12em]">
          DOSSIER
        </span>
      </Link>

      <nav className="hidden items-center gap-8 font-body text-sm text-ink-soft sm:flex">
        <a href="#workflows" className="transition hover:text-paper">
          Workflows
        </a>
        <a href="#architecture" className="transition hover:text-paper">
          Architecture
        </a>
        <a
          href="https://github.com/Mohit-Kirtane/dossier"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 transition hover:text-paper"
        >
          <GithubMark className="h-4 w-4" />
          Source
        </a>
      </nav>

      <Link
        to="/app"
        className="rounded-md bg-ochre px-4 py-2 font-body text-sm font-medium text-ink transition hover:bg-ochre-deep hover:text-paper"
      >
        Open the copilot
      </Link>
    </header>
  );
}
