import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { deploymentsApi } from "../api/deployments";
import { monitoringApi } from "../api/monitoring";
import { ApiError } from "../api/client";
import { PageHeader } from "../components/shared/PageHeader";
import { StatusBadge } from "../components/shared/StatusBadge";
import { Button } from "../components/ui/Button";
import type {
  DeploymentEventResponse,
  DeploymentResponse,
  InferenceLogResponse,
} from "../types/deployments";
import { getDirectEndpoint, getPredictEndpoint } from "../utils/api";
import { formatDate } from "../utils/format";

type Tab = "overview" | "metrics" | "logs" | "history";

export function DeploymentDetailPage() {
  const { deploymentId } = useParams();
  const [deployment, setDeployment] = useState<DeploymentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const [isActing, setIsActing] = useState(false);

  const [stats, setStats] = useState({ request_count: 0, error_count: 0, avg_latency_ms: 0 });
  const [containerLogs, setContainerLogs] = useState("");
  const [inferenceLogs, setInferenceLogs] = useState<InferenceLogResponse[]>([]);
  const [events, setEvents] = useState<DeploymentEventResponse[]>([]);

  async function loadDeployment() {
    if (!deploymentId) {
      return;
    }
    try {
      const response = await deploymentsApi.get(deploymentId);
      setDeployment(response);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load deployment");
    }
  }

  async function loadTabData(tab: Tab) {
    if (!deploymentId) {
      return;
    }
    try {
      if (tab === "metrics") {
        const response = await monitoringApi.deploymentStats(deploymentId);
        setStats(response);
      } else if (tab === "logs") {
        const [deployLogs, inferLogs] = await Promise.all([
          deploymentsApi.logs(deploymentId, 200),
          deploymentsApi.inferenceLogs(deploymentId),
        ]);
        setContainerLogs(deployLogs.logs);
        setInferenceLogs(inferLogs);
      } else if (tab === "history") {
        const response = await deploymentsApi.events(deploymentId);
        setEvents(response);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load tab data");
    }
  }

  useEffect(() => {
    void loadDeployment();
    const interval = window.setInterval(() => {
      void loadDeployment();
    }, 5000);
    return () => window.clearInterval(interval);
  }, [deploymentId]);

  useEffect(() => {
    if (activeTab !== "overview") {
      void loadTabData(activeTab);
    }
  }, [activeTab, deploymentId]);

  async function runAction(action: "stop" | "redeploy" | "rollback" | "delete") {
    if (!deploymentId) {
      return;
    }
    setIsActing(true);
    setError(null);
    try {
      if (action === "stop") {
        const response = await deploymentsApi.stop(deploymentId);
        setDeployment(response);
      } else if (action === "redeploy") {
        const response = await deploymentsApi.redeploy(deploymentId);
        setDeployment(response);
      } else if (action === "rollback") {
        const response = await deploymentsApi.rollback(deploymentId);
        setDeployment(response);
      } else if (action === "delete") {
        await deploymentsApi.remove(deploymentId);
        window.location.href = "/deployments";
        return;
      }
      if (activeTab !== "overview") {
        void loadTabData(activeTab);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : `Failed to ${action} deployment`);
    } finally {
      setIsActing(false);
    }
  }

  function copyToClipboard(value: string) {
    void navigator.clipboard.writeText(value);
  }

  if (!deploymentId) {
    return null;
  }

  const predictEndpoint = getPredictEndpoint(deploymentId);
  const directEndpoint = getDirectEndpoint(deployment?.host_port ?? null);
  const isRunning = deployment?.status === "running";
  const canRedeploy =
    deployment?.status === "running" ||
    deployment?.status === "stopped" ||
    deployment?.status === "failed";

  const tabs: { id: Tab; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "metrics", label: "Metrics" },
    { id: "logs", label: "Logs" },
    { id: "history", label: "History" },
  ];

  return (
    <section className="space-y-6">
      <PageHeader
        title={deployment?.name ?? "Deployment"}
        description="Deployment status, metrics, logs, and lifecycle controls."
      />

      {error ? <p className="text-sm text-rose-400">{error}</p> : null}

      <div className="flex gap-2 border-b border-slate-800">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm ${
              activeTab === tab.id
                ? "border-b-2 border-indigo-500 text-indigo-400"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {!deployment ? (
        <p className="text-sm text-slate-400">Loading deployment...</p>
      ) : (
        <>
          {activeTab === "overview" ? (
            <>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                  <h2 className="mb-4 text-lg font-medium">Status</h2>
                  <dl className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-slate-400">Lifecycle</dt>
                      <dd>
                        <StatusBadge status={deployment.status} />
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-slate-400">Health</dt>
                      <dd>
                        <StatusBadge status={deployment.health_status} />
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-slate-400">Model version</dt>
                      <dd className="font-mono text-xs">{deployment.model_version_id.slice(0, 8)}…</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-slate-400">Deployed at</dt>
                      <dd>{formatDate(deployment.deployed_at)}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-slate-400">Host port</dt>
                      <dd>{deployment.host_port ?? "-"}</dd>
                    </div>
                  </dl>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                  <h2 className="mb-4 text-lg font-medium">Endpoints</h2>
                  {isRunning ? (
                    <div className="space-y-4 text-sm">
                      <div>
                        <p className="mb-1 text-slate-400">Platform predict API (JWT or API key)</p>
                        <div className="flex gap-2">
                          <code className="flex-1 overflow-x-auto rounded bg-slate-950 px-3 py-2 text-xs">
                            POST {predictEndpoint}
                          </code>
                          <Button type="button" onClick={() => copyToClipboard(predictEndpoint)}>
                            Copy
                          </Button>
                        </div>
                      </div>
                      {directEndpoint ? (
                        <div>
                          <p className="mb-1 text-slate-400">Direct inference (debug)</p>
                          <div className="flex gap-2">
                            <code className="flex-1 overflow-x-auto rounded bg-slate-950 px-3 py-2 text-xs">
                              POST {directEndpoint}
                            </code>
                            <Button type="button" onClick={() => copyToClipboard(directEndpoint)}>
                              Copy
                            </Button>
                          </div>
                        </div>
                      ) : null}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400">Endpoints are available when deployment is running.</p>
                  )}
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                {isRunning ? (
                  <Link to={`/deployments/${deploymentId}/playground`}>
                    <Button>Open Playground</Button>
                  </Link>
                ) : null}
                {canRedeploy ? (
                  <Button type="button" disabled={isActing} onClick={() => void runAction("redeploy")}>
                    {isActing ? "Working..." : "Redeploy"}
                  </Button>
                ) : null}
                {canRedeploy ? (
                  <Button type="button" disabled={isActing} onClick={() => void runAction("rollback")}>
                    Rollback
                  </Button>
                ) : null}
                {deployment.status === "running" || deployment.status === "failed" ? (
                  <Button
                    type="button"
                    onClick={() => void runAction("stop")}
                    disabled={isActing}
                    className="!bg-rose-700 hover:!bg-rose-600"
                  >
                    Stop
                  </Button>
                ) : null}
                <Button
                  type="button"
                  onClick={() => void runAction("delete")}
                  disabled={isActing}
                  className="!bg-slate-700 hover:!bg-slate-600"
                >
                  Delete
                </Button>
                <Link
                  to="/deployments"
                  className="inline-flex items-center text-sm text-indigo-400 hover:text-indigo-300"
                >
                  Back to deployments
                </Link>
              </div>
            </>
          ) : null}

          {activeTab === "metrics" ? (
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm text-slate-400">Request count</p>
                <p className="mt-2 text-3xl font-semibold">{stats.request_count}</p>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm text-slate-400">Error count</p>
                <p className="mt-2 text-3xl font-semibold">{stats.error_count}</p>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm text-slate-400">Avg latency</p>
                <p className="mt-2 text-3xl font-semibold">{stats.avg_latency_ms.toFixed(1)} ms</p>
              </div>
            </div>
          ) : null}

          {activeTab === "logs" ? (
            <div className="space-y-6">
              <div>
                <h2 className="mb-2 text-lg font-medium">Deployment logs</h2>
                <pre className="max-h-64 overflow-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-slate-300">
                  {containerLogs || "No container logs available."}
                </pre>
              </div>
              <div>
                <h2 className="mb-2 text-lg font-medium">Inference logs</h2>
                {inferenceLogs.length === 0 ? (
                  <p className="text-sm text-slate-400">No inference requests logged yet.</p>
                ) : (
                  <table className="min-w-full text-left text-sm">
                    <thead className="border-b border-slate-800 text-slate-400">
                      <tr>
                        <th className="px-4 py-2 font-medium">Time</th>
                        <th className="px-4 py-2 font-medium">Status</th>
                        <th className="px-4 py-2 font-medium">Latency</th>
                        <th className="px-4 py-2 font-medium">Error</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {inferenceLogs.map((log) => (
                        <tr key={log.id}>
                          <td className="px-4 py-2 text-slate-400">{formatDate(log.created_at)}</td>
                          <td className="px-4 py-2">{log.status_code}</td>
                          <td className="px-4 py-2">{log.latency_ms.toFixed(1)} ms</td>
                          <td className="px-4 py-2 text-rose-400">{log.error_message ?? "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          ) : null}

          {activeTab === "history" ? (
            <div className="rounded-lg border border-slate-800 bg-slate-900">
              {events.length === 0 ? (
                <p className="p-6 text-sm text-slate-400">No deployment events yet.</p>
              ) : (
                <ul className="divide-y divide-slate-800">
                  {events.map((event) => (
                    <li key={event.id} className="px-6 py-4 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-medium capitalize">{event.event_type}</span>
                        <span className="text-slate-500">{formatDate(event.created_at)}</span>
                      </div>
                      <p className="mt-1 text-slate-400">{event.message}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : null}
        </>
      )}
    </section>
  );
}
