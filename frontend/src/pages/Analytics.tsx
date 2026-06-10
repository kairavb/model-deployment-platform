import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { analyticsApi, type TrendsResponse, type UsageResponse } from "../api/analytics";
import { ApiError } from "../api/client";
import { SimpleBarChart } from "../components/shared/SimpleBarChart";
import { PageHeader } from "../components/shared/PageHeader";

function formatDayLabel(date: string) {
  const parsed = new Date(date);
  return parsed.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function AnalyticsPage() {
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [trends, setTrends] = useState<TrendsResponse | null>(null);
  const [days, setDays] = useState(7);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [usageResponse, trendsResponse] = await Promise.all([
          analyticsApi.usage(),
          analyticsApi.trends(days),
        ]);
        setUsage(usageResponse);
        setTrends(trendsResponse);
        setError(null);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Failed to load analytics");
      }
    }
    void load();
  }, [days]);

  const trendLabels = trends?.points.map((point) => formatDayLabel(point.date)) ?? [];
  const requestValues = trends?.points.map((point) => point.request_count) ?? [];
  const errorValues = trends?.points.map((point) => point.error_count) ?? [];

  return (
    <section className="space-y-8">
      <PageHeader
        title="Analytics"
        description="Usage overview, request trends, and error trends across your deployments."
      />

      {error ? <p className="text-sm text-rose-400">{error}</p> : null}

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Total requests</p>
          <p className="mt-2 text-3xl font-semibold">{usage?.total_requests ?? 0}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Total errors</p>
          <p className="mt-2 text-3xl font-semibold">{usage?.total_errors ?? 0}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">Avg latency</p>
          <p className="mt-2 text-3xl font-semibold">
            {(usage?.avg_latency_ms ?? 0).toFixed(1)} ms
          </p>
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-medium">Request trends</h2>
          <select
            className="rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-sm"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </div>
        <SimpleBarChart
          labels={trendLabels}
          series={[
            {
              label: "Requests",
              values: requestValues,
              colorClass: "bg-indigo-500",
            },
          ]}
          emptyMessage="Run predictions in the playground to see request trends."
        />
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-lg font-medium">Error trends</h2>
        <SimpleBarChart
          labels={trendLabels}
          series={[
            {
              label: "Errors",
              values: errorValues,
              colorClass: "bg-rose-500",
            },
          ]}
          emptyMessage="No errors recorded in this period."
        />
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-lg font-medium">Usage by deployment</h2>
        {!usage || usage.deployments.length === 0 ? (
          <p className="text-sm text-slate-400">No deployment usage yet.</p>
        ) : (
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-slate-800 text-slate-400">
              <tr>
                <th className="px-4 py-2 font-medium">Deployment</th>
                <th className="px-4 py-2 font-medium">Requests</th>
                <th className="px-4 py-2 font-medium">Errors</th>
                <th className="px-4 py-2 font-medium">Avg latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {usage.deployments.map((item) => (
                <tr key={item.deployment_id}>
                  <td className="px-4 py-3">
                    <Link
                      to={`/deployments/${item.deployment_id}`}
                      className="text-indigo-400 hover:text-indigo-300"
                    >
                      {item.deployment_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3">{item.request_count}</td>
                  <td className="px-4 py-3">{item.error_count}</td>
                  <td className="px-4 py-3">{item.avg_latency_ms.toFixed(1)} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
