import { Link, Outlet } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { Button } from "../ui/Button";

const DOCS_URL = import.meta.env.VITE_DOCS_URL ?? "http://localhost:8080/docs";

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-lg font-semibold">
            AI Platform
          </Link>
          <nav className="flex items-center gap-4 text-sm text-slate-300">
            <Link to="/models">Models</Link>
            <Link to="/deployments">Deployments</Link>
            <Link to="/playground">Playground</Link>
            <Link to="/analytics">Analytics</Link>
            <Link to="/api-keys">API Keys</Link>
            <a href={DOCS_URL} target="_blank" rel="noreferrer" className="text-slate-300 hover:text-white">
              API Docs
            </a>
            {user ? <span className="text-slate-400">{user.email}</span> : null}
            <Button type="button" onClick={logout} className="!px-3 !py-1.5">
              Sign out
            </Button>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
