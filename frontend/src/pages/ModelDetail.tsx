import { useParams } from "react-router-dom";

import { PageHeader } from "../components/shared/PageHeader";

export function ModelDetailPage() {
  const { modelId } = useParams();

  return (
    <section>
      <PageHeader
        title={`Model ${modelId ?? ""}`}
        description="Version history and deployment actions."
      />
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
        Model detail UI will be implemented in Phase 1.
      </div>
    </section>
  );
}
