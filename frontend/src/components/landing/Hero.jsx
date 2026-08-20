import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { LedgerTrace } from "./LedgerTrace.jsx";
import { GithubMark } from "../brand/GithubMark.jsx";

export function Hero() {
  return (
    <section className="mx-auto grid w-full max-w-6xl grid-cols-1 items-center gap-16 px-6 pt-8 pb-24 sm:px-10 lg:grid-cols-[1.05fr_1fr] lg:gap-12 lg:pt-16">
      <div>
        <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ochre">
          DOCUMENT INTELLIGENCE · MODULE 01
        </p>
        <h1 className="mt-5 font-display text-[2.75rem] leading-[1.08] font-medium text-paper sm:text-[3.4rem]">
          Every answer,
          <br />
          <span className="italic text-ochre">filed and cited.</span>
        </h1>
        <p className="mt-6 max-w-md font-body text-base leading-relaxed text-ink-soft">
          Upload a document, ask a question in plain language, and get an answer grounded in the
          exact passage it came from — not a guess. Built as the first module of a larger
          enterprise knowledge platform.
        </p>

        <div className="mt-9 flex flex-wrap items-center gap-4">
          <Link
            to="/app"
            className="group flex items-center gap-2 rounded-md bg-ochre px-5 py-3 font-body text-sm font-medium text-ink transition hover:bg-ochre-deep hover:text-paper"
          >
            Open the copilot
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
          </Link>
          <a
            href="https://github.com/Mohit-Kirtane/dossier"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-md border border-rule px-5 py-3 font-body text-sm font-medium text-paper transition hover:border-ink-soft"
          >
            <GithubMark className="h-4 w-4" />
            View source
          </a>
        </div>
      </div>

      <div className="flex justify-center lg:justify-end">
        <LedgerTrace animate />
      </div>
    </section>
  );
}
