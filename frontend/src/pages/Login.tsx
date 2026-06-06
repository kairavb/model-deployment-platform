import { PageHeader } from "../components/shared/PageHeader";

export function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <section className="w-full max-w-md rounded-lg border border-slate-800 bg-slate-900 p-6">
        <PageHeader title="Sign in" description="Authentication UI skeleton." />
        <p className="text-sm text-slate-400">Login form will be implemented in Phase 1.</p>
      </section>
    </div>
  );
}
