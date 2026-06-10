import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { deploymentsApi } from "../api/deployments";
import { ApiError } from "../api/client";
import { PageHeader } from "../components/shared/PageHeader";
import { StatusBadge } from "../components/shared/StatusBadge";
import type { DeploymentResponse } from "../types/deployments";
import { formatDate } from "../utils/format";

export function DeploymentsPage() {
  const [deployments, setDeployments] = useState<DeploymentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadDeployments() {
    setIsLoading(true);
    setError(null);
    try {
      const response = await deploymentsApi.list();
      setDeployments(response.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load deployments");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadDeployments();
    const interval = window.setInterval(() => {
      void loadDeployments();
    }, 5000);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <section>
      <PageHeader title="Deployments" description="Monitor deployment status and endpoints." />

      <div className="rounded-lg border border-slate-800 bg-slate-900">
        {isLoading ? <p className="p-6 text-sm text-slate-400">Loading deployments...</p> : null}
        {error ? <p className="p-6 text-sm text-rose-400">{error}</p> : null}

        {!isLoading && deployments.length === 0 ? (
          <p className="p-6 text-sm text-slate-400">
            No deployments yet.{" "}
            <Link to="/models" className="text-indigo-400 hover:text-indigo-300">
              Deploy a model
            </Link>
          </p>
        ) : null}

        {!isLoading && deployments.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-slate-800 text-slate-400">
                <tr>
                  <th className="px-6 py-3 font-medium">Name</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Health</th>
                  <th className="px-6 py-3 font-medium">Port</th>
                  <th className="px-6 py-3 font-medium">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {deployments.map((deployment) => (
                  <tr key={deployment.id}>
                    <td className="px-6 py-4">
                      <Link
                        to={`/deployments/${deployment.id}`}
                        className="font-medium text-indigo-400 hover:text-indigo-300"
                      >
                        {deployment.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={deployment.status} />
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={deployment.health_status} />
                    </td>
                    <td className="px-6 py-4 text-slate-300">{deployment.host_port ?? "-"}</td>
                    <td className="px-6 py-4 text-slate-400">{formatDate(deployment.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </section>
  );
}
