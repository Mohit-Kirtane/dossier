import { Link, useLocation } from "react-router-dom";

const MODULES = [
  { path: "/app", label: "Document intel" },
  { path: "/app/database-chat", label: "Database chat" },
  { path: "/app/policy-chat", label: "Policy retrieval" },
];

export function ModuleTabs() {
  const { pathname } = useLocation();

  return (
    <nav className="flex gap-4 border-b border-rule pb-4">
      {MODULES.map((m) => {
        const active = pathname === m.path;
        return (
          <Link
            key={m.path}
            to={m.path}
            className={`font-mono text-[11px] font-medium tracking-[0.12em] transition ${
              active ? "text-ochre" : "text-ink-soft hover:text-paper"
            }`}
          >
            {m.label.toUpperCase()}
          </Link>
        );
      })}
    </nav>
  );
}
