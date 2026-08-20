import { Link } from "react-router-dom";
import { Activity, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext.jsx";

export function UserMenu() {
  const { user, logout } = useAuth();
  if (!user) return null;

  const initials = user.name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="flex items-center justify-between gap-2 border-t border-rule pt-4">
      <div className="flex min-w-0 items-center gap-2">
        {user.avatar_url ? (
          <img src={user.avatar_url} alt="" className="h-6 w-6 shrink-0 rounded-full" />
        ) : (
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ochre/20 font-mono text-[10px] font-medium text-ochre-deep">
            {initials}
          </span>
        )}
        <div className="min-w-0">
          <p className="truncate font-body text-xs font-medium text-paper">{user.name}</p>
          {user.is_admin && (
            <p className="font-mono text-[9px] tracking-wide text-ochre">ADMIN</p>
          )}
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {user.is_admin && (
          <Link to="/app/activity" title="Activity" className="text-ink-soft transition hover:text-ochre">
            <Activity className="h-4 w-4" />
          </Link>
        )}
        <button
          type="button"
          onClick={logout}
          title="Log out"
          className="text-ink-soft transition hover:text-rose-400"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
