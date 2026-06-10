import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { deploymentsApi } from "../api/deployments";
import { monitoringApi } from "../api/monitoring";
import { modelsApi } from "../api/models";
import { PageHeader } from "../components/shared/PageHeader";
import { StatusBadge } from "../components/shared/StatusBadge";
import { useAuth } from "../context/AuthContext";

export function DashboardPage() {
  const { user } = useAuth();
  const [modelCount, setModelCount] = useState(0);
  const [activeDeployments, setActiveDeployments] = useState(0);
  const [stats, setStats] = useState({ request_count: 0, error_count: 0, avg_latency_ms: 0 });
  const [recentDeployments, setRecentDeployments] = useState<
    Awaited<ReturnType<typeof deploymentsApi.list>>["items"]
  >([]);

  useEffect(() => {
    async function load() {
      const [models, deployments, userStats] = await Promise.all([
        modelsApi.list(1, 5),
        deploymentsApi.list(1, 5),
        monitoringApi.userStats().catch(() => ({
          request_count: 0,
          error_count: 0,
          avg_latency_ms: 0,
        })),
      ]);
      setModelCount(models.total);
      setRecentDeployments(deployments.items);
      setStats(userStats);
      setActiveDeployments(
        deployments.items.filter((item) => item.status === "running" || item.status === "starting").length,
      );
    }
    void load();
  }, []);

  return (
    <section className="space-y-8">
      <PageHeader
        title="Dashboard"
        description={user ? `Welcome back, ${user.display_name ?? user.email}` : "Overview"}
      />

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Models</p>
          <p className="mt-2 text-3xl font-semibold">{modelCount}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Active deployments</p>
          <p className="mt-2 text-3xl font-semibold">{activeDeployments}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Quick actions</p>
          <div className="mt-3 flex flex-col gap-2 text-sm">
            <Link to="/models" className="text-indigo-400 hover:text-indigo-300">
              Upload a model
            </Link>
            <Link to="/deployments" className="text-indigo-400 hover:text-indigo-300">
              View deployments
            </Link>
            <Link to="/playground" className="text-indigo-400 hover:text-indigo-300">
              Open playground
            </Link>
            <Link to="/analytics" className="text-indigo-400 hover:text-indigo-300">
              View analytics
            </Link>
            <Link to="/api-keys" className="text-indigo-400 hover:text-indigo-300">
              Manage API keys
            </Link>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Total requests</p>
          <p className="mt-2 text-3xl font-semibold">{stats.request_count}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Errors</p>
          <p className="mt-2 text-3xl font-semibold">{stats.error_count}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Avg latency</p>
          <p className="mt-2 text-3xl font-semibold">{stats.avg_latency_ms.toFixed(1)} ms</p>
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-lg font-medium">Recent deployments</h2>
        {recentDeployments.length === 0 ? (
          <p className="text-sm text-slate-400">No deployments yet.</p>
        ) : (
          <ul className="space-y-3">
            {recentDeployments.map((deployment) => (
              <li key={deployment.id} className="flex items-center justify-between text-sm">
                <Link
                  to={`/deployments/${deployment.id}`}
                  className="text-indigo-400 hover:text-indigo-300"
                >
                  {deployment.name}
                </Link>
                <div className="flex items-center gap-3">
                  <StatusBadge status={deployment.health_status} />
                  <StatusBadge status={deployment.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
