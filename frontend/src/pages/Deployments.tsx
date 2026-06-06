import { PageHeader } from "../components/shared/PageHeader";

export function DeploymentsPage() {
  return (
    <section>
      <PageHeader title="Deployments" description="Monitor active and historical deployments." />
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
        Deployment list UI will be implemented in Phase 2.
      </div>
    </section>
  );
}
