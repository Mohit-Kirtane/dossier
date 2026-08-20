import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Logo } from "../components/brand/Logo.jsx";
import { GoogleMark } from "../components/brand/GoogleMark.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { googleLoginUrl, registerUser } from "../lib/authApi.js";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const { refresh } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await registerUser(email, password, name);
      await refresh();
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-6">
      <div className="w-full max-w-sm">
        <Link to="/" className="mb-8 flex items-center justify-center gap-2 text-paper transition hover:text-ochre">
          <Logo className="h-6 w-6" />
          <span className="font-mono text-[12px] font-medium tracking-[0.12em]">
            DOSSIER
          </span>
        </Link>

        <div className="rounded-lg border border-rule bg-ink-raised p-7">
          <p className="font-mono text-[11px] font-medium tracking-[0.18em] text-ochre">CREATE ACCOUNT</p>
          <h1 className="mt-2 font-display text-xl font-medium text-paper">Get started</h1>

          <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3">
            <input
              type="text"
              required
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="rounded-md border border-rule bg-ink px-3.5 py-2.5 font-body text-sm text-paper outline-none placeholder:text-ink-soft focus:border-ochre"
            />
            <input
              type="email"
              required
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="rounded-md border border-rule bg-ink px-3.5 py-2.5 font-body text-sm text-paper outline-none placeholder:text-ink-soft focus:border-ochre"
            />
            <input
              type="password"
              required
              placeholder="Password (min. 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="rounded-md border border-rule bg-ink px-3.5 py-2.5 font-body text-sm text-paper outline-none placeholder:text-ink-soft focus:border-ochre"
            />
            {error && <p className="font-body text-xs text-rose-400">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="mt-1 rounded-md bg-ochre px-4 py-2.5 font-body text-sm font-medium text-ink transition hover:bg-ochre-deep hover:text-paper disabled:opacity-50"
            >
              {submitting ? "Creating account…" : "Create account"}
            </button>
          </form>

          <div className="my-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-rule" />
            <span className="font-mono text-[10px] tracking-wide text-ink-soft">OR</span>
            <div className="h-px flex-1 bg-rule" />
          </div>

          <a
            href={googleLoginUrl}
            className="flex items-center justify-center gap-2.5 rounded-md border border-rule bg-paper px-4 py-2.5 font-body text-sm font-medium text-ink transition hover:border-ochre-deep"
          >
            <GoogleMark className="h-4 w-4" />
            Continue with Google
          </a>
        </div>

        <p className="mt-5 text-center font-body text-sm text-ink-soft">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-ochre hover:text-ochre-deep">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
