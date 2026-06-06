import { useParams } from "react-router-dom";

import { PageHeader } from "../components/shared/PageHeader";

export function PlaygroundPage() {
  const { deploymentId } = useParams();

  return (
    <section>
      <PageHeader
        title="Prediction Playground"
        description={`Test predictions for deployment ${deploymentId ?? ""}.`}
      />
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
        Playground UI will be implemented in Phase 3.
      </div>
    </section>
  );
}
