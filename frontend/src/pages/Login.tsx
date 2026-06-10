import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { PageHeader } from "../components/shared/PageHeader";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, login, register } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (isRegisterMode) {
        await register(email, password, displayName || undefined);
      } else {
        await login({ email, password });
      }
      navigate("/");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <section className="w-full max-w-md rounded-lg border border-slate-800 bg-slate-900 p-6">
        <PageHeader
          title={isRegisterMode ? "Create account" : "Sign in"}
          description="Deploy and manage ML models locally."
        />

        <form className="space-y-4" onSubmit={handleSubmit}>
          {isRegisterMode ? (
            <div>
              <label className="mb-1 block text-sm text-slate-400">Display name</label>
              <Input
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                placeholder="Optional"
              />
            </div>
          ) : null}

          <div>
            <label className="mb-1 block text-sm text-slate-400">Email</label>
            <Input
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm text-slate-400">Password</label>
            <Input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Minimum 8 characters"
            />
          </div>

          {error ? <p className="text-sm text-rose-400">{error}</p> : null}

          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? "Please wait..." : isRegisterMode ? "Create account" : "Sign in"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-400">
          {isRegisterMode ? "Already have an account?" : "Need an account?"}{" "}
          <button
            type="button"
            className="text-indigo-400 hover:text-indigo-300"
            onClick={() => {
              setIsRegisterMode((value) => !value);
              setError(null);
            }}
          >
            {isRegisterMode ? "Sign in" : "Create one"}
          </button>
        </p>

        <p className="mt-2 text-center text-sm">
          <Link to="/" className="text-slate-500 hover:text-slate-400">
            Back to home
          </Link>
        </p>
      </section>
    </div>
  );
}
