import { PageHeader } from "../components/shared/PageHeader";

export function DashboardPage() {
  return (
    <section>
      <PageHeader
        title="Dashboard"
        description="Overview of models, deployments, and recent activity."
      />
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
        Dashboard metrics will be implemented in a later phase.
      </div>
    </section>
  );
}
