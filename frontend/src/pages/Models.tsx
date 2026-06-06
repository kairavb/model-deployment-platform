import { PageHeader } from "../components/shared/PageHeader";

export function ModelsPage() {
  return (
    <section>
      <PageHeader title="Models" description="Upload and manage ML model versions." />
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
        Model list UI will be implemented in Phase 1.
      </div>
    </section>
  );
}
