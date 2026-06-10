import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { deploymentsApi } from "../api/deployments";
import { ApiError } from "../api/client";
import { PageHeader } from "../components/shared/PageHeader";
import { StatusBadge } from "../components/shared/StatusBadge";
import { Button } from "../components/ui/Button";
import type { DeploymentResponse } from "../types/deployments";

const EXAMPLES = [
  { label: "Iris sample", value: "[[5.1, 3.5, 1.4, 0.2]]" },
  { label: "Batch (2 rows)", value: "[[5.1, 3.5, 1.4, 0.2], [6.2, 3.4, 5.4, 2.3]]" },
  { label: "Full payload", value: '{\n  "inputs": [[5.1, 3.5, 1.4, 0.2]]\n}' },
];

interface RequestHistoryItem {
  id: string;
  status: "success" | "error";
  latencyMs: number;
  summary: string;
}

export function PlaygroundPage() {
  const { deploymentId: routeDeploymentId } = useParams();
  const navigate = useNavigate();
  const [deployments, setDeployments] = useState<DeploymentResponse[]>([]);
  const [deploymentId, setDeploymentId] = useState(routeDeploymentId ?? "");
  const [deployment, setDeployment] = useState<DeploymentResponse | null>(null);
  const [inputs, setInputs] = useState(EXAMPLES[0].value);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorHint, setErrorHint] = useState<string | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<RequestHistoryItem[]>([]);

  useEffect(() => {
    async function loadDeployments() {
      try {
        const response = await deploymentsApi.list(1, 100, "running");
        setDeployments(response.items);
        if (!routeDeploymentId && response.items.length > 0) {
          setDeploymentId(response.items[0].id);
        }
      } catch {
        // Playground still works when a deployment id is in the URL.
      }
    }
    void loadDeployments();
  }, [routeDeploymentId]);

  useEffect(() => {
    if (routeDeploymentId) {
      setDeploymentId(routeDeploymentId);
    }
  }, [routeDeploymentId]);

  useEffect(() => {
    if (!deploymentId) {
      setDeployment(null);
      return;
    }
    async function loadDeployment() {
      try {
        const response = await deploymentsApi.get(deploymentId);
        setDeployment(response);
      } catch {
        setDeployment(null);
      }
    }
    void loadDeployment();
  }, [deploymentId]);

  function handleDeploymentChange(nextId: string) {
    setDeploymentId(nextId);
    navigate(nextId ? `/deployments/${nextId}/playground` : "/playground", { replace: true });
  }

  async function handlePredict(event: FormEvent) {
    event.preventDefault();
    if (!deploymentId) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setErrorHint(null);
    setRequestId(null);
    setResult(null);
    setLatencyMs(null);

    const start = performance.now();
    try {
      const parsed = JSON.parse(inputs) as unknown;
      const payload = Array.isArray(parsed) ? { inputs: parsed } : parsed;
      const response = await deploymentsApi.predict(deploymentId, payload as { inputs: unknown[] });
      const elapsed = performance.now() - start;
      setLatencyMs(elapsed);
      setResult(JSON.stringify(response, null, 2));
      setHistory((prev) => [
        {
          id: crypto.randomUUID(),
          status: "success",
          latencyMs: elapsed,
          summary: "Prediction succeeded",
        },
        ...prev.slice(0, 4),
      ]);
    } catch (err) {
      const elapsed = performance.now() - start;
      setLatencyMs(elapsed);
      if (err instanceof SyntaxError) {
        setError("Invalid JSON input.");
        setErrorHint('Use a JSON array like [[5.1, 3.5, 1.4, 0.2]] or {"inputs": [...]}.');
      } else if (err instanceof ApiError) {
        setError(err.message);
        setErrorHint(err.hint ?? null);
        setRequestId(err.requestId ?? null);
      } else {
        setError("Prediction failed.");
      }
      setHistory((prev) => [
        {
          id: crypto.randomUUID(),
          status: "error",
          latencyMs: elapsed,
          summary: err instanceof ApiError ? err.message : "Prediction failed",
        },
        ...prev.slice(0, 4),
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Inference Playground"
        description="Test deployed models with JSON inputs and inspect responses in real time."
      />

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <label className="mb-1 block text-sm text-slate-400">Deployment</label>
          <select
            className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            value={deploymentId}
            onChange={(e) => handleDeploymentChange(e.target.value)}
          >
            <option value="">Select a running deployment</option>
            {deployments.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name} (port {item.host_port ?? "-"})
              </option>
            ))}
          </select>
          {deployment ? (
            <div className="mt-4 flex items-center gap-3 text-sm">
              <StatusBadge status={deployment.status} />
              <StatusBadge status={deployment.health_status} />
            </div>
          ) : null}
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
          <p className="mb-2 font-medium text-slate-200">Tips</p>
          <ul className="list-disc space-y-1 pl-5">
            <li>Deployments must be in the <strong>running</strong> state.</li>
            <li>Sklearn Iris-style models expect numeric feature rows.</li>
            <li>Requests are logged for analytics and appear in deployment metrics.</li>
          </ul>
        </div>
      </div>

      <form onSubmit={handlePredict} className="space-y-4 rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <button
              key={example.label}
              type="button"
              onClick={() => setInputs(example.value)}
              className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300 hover:border-indigo-500 hover:text-indigo-300"
            >
              {example.label}
            </button>
          ))}
        </div>

        <div>
          <label className="mb-1 block text-sm text-slate-400">Inputs JSON</label>
          <textarea
            className="h-44 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm"
            value={inputs}
            onChange={(e) => setInputs(e.target.value)}
            spellCheck={false}
          />
        </div>

        <Button type="submit" disabled={isLoading || !deploymentId || deployment?.status !== "running"}>
          {isLoading ? "Predicting..." : "Run prediction"}
        </Button>
      </form>

      {latencyMs !== null ? (
        <p className="text-sm text-slate-400">Round-trip latency: {latencyMs.toFixed(1)} ms</p>
      ) : null}

      {error ? (
        <div className="rounded-lg border border-rose-900/50 bg-rose-950/20 p-4 text-sm text-rose-300">
          <p>{error}</p>
          {errorHint ? <p className="mt-1 text-rose-200/80">{errorHint}</p> : null}
          {requestId ? <p className="mt-1 font-mono text-xs text-rose-200/60">request_id: {requestId}</p> : null}
        </div>
      ) : null}

      {result ? (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-2 text-lg font-medium">Response</h2>
          <pre className="overflow-x-auto rounded bg-slate-950 p-4 text-sm">{result}</pre>
        </div>
      ) : null}

      {history.length > 0 ? (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-3 text-lg font-medium">Recent requests</h2>
          <ul className="space-y-2 text-sm">
            {history.map((item) => (
              <li key={item.id} className="flex justify-between text-slate-400">
                <span className={item.status === "error" ? "text-rose-400" : "text-emerald-400"}>
                  {item.summary}
                </span>
                <span>{item.latencyMs.toFixed(1)} ms</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="flex gap-4 text-sm">
        <Link to="/playground" className="text-indigo-400 hover:text-indigo-300">
          Playground hub
        </Link>
        {deploymentId ? (
          <Link
            to={`/deployments/${deploymentId}`}
            className="text-indigo-400 hover:text-indigo-300"
          >
            Back to deployment
          </Link>
        ) : null}
      </div>
    </section>
  );
}
