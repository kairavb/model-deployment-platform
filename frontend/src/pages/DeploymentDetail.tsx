import { Link, useParams } from "react-router-dom";

import { PageHeader } from "../components/shared/PageHeader";
import { Button } from "../components/ui/Button";

export function DeploymentDetailPage() {
  const { deploymentId } = useParams();

  return (
    <section>
      <PageHeader
        title={`Deployment ${deploymentId ?? ""}`}
        description="Health, logs, endpoint URLs, and lifecycle controls."
      />
      <div className="mb-4">
        <Link to={`/deployments/${deploymentId}/playground`}>
          <Button>Open Playground</Button>
        </Link>
      </div>
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
        Deployment detail UI will be implemented in Phase 2.
      </div>
    </section>
  );
}
