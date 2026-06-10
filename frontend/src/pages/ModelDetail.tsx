import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { deploymentsApi } from "../api/deployments";
import { ApiError } from "../api/client";
import { modelsApi } from "../api/models";
import { PageHeader } from "../components/shared/PageHeader";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import type { ModelResponse, ModelVersionResponse } from "../types/models";
import { formatDate } from "../utils/format";

export function ModelDetailPage() {
  const { modelId } = useParams();
  const navigate = useNavigate();
  const [model, setModel] = useState<ModelResponse | null>(null);
  const [versions, setVersions] = useState<ModelVersionResponse[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState("");
  const [deploymentName, setDeploymentName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isDeploying, setIsDeploying] = useState(false);

  useEffect(() => {
    if (!modelId) {
      return;
    }

    async function load(currentModelId: string) {
      try {
        const [modelResponse, versionResponse] = await Promise.all([
          modelsApi.get(currentModelId),
          modelsApi.listVersions(currentModelId),
        ]);
        setModel(modelResponse);
        setVersions(versionResponse);
        if (versionResponse.length > 0) {
          setSelectedVersionId(versionResponse[0].id);
          setDeploymentName(`${modelResponse.name}-deploy`);
        }
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Failed to load model");
      }
    }

    void load(modelId);
  }, [modelId]);

  async function handleDeploy(event: FormEvent) {
    event.preventDefault();
    if (!selectedVersionId) {
      return;
    }

    setIsDeploying(true);
    setError(null);

    try {
      const deployment = await deploymentsApi.create({
        model_version_id: selectedVersionId,
        name: deploymentName,
      });
      navigate(`/deployments/${deployment.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Deployment failed");
    } finally {
      setIsDeploying(false);
    }
  }

  if (!modelId) {
    return null;
  }

  return (
    <section className="space-y-8">
      <PageHeader
        title={model?.name ?? "Model"}
        description={model?.description ?? "Model versions and deployment."}
      />

      {error ? <p className="text-sm text-rose-400">{error}</p> : null}

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-lg font-medium">Versions</h2>
        {versions.length === 0 ? (
          <p className="text-sm text-slate-400">No versions uploaded yet.</p>
        ) : (
          <ul className="space-y-2 text-sm">
            {versions.map((version) => (
              <li key={version.id} className="flex justify-between border-b border-slate-800 py-2">
                <span>
                  v{version.version_number} · {(version.file_size_bytes / 1024).toFixed(1)} KB ·{" "}
                  {version.status}
                </span>
                <span className="text-slate-500">{formatDate(version.created_at)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {versions.length > 0 ? (
        <form onSubmit={handleDeploy} className="rounded-lg border border-slate-800 bg-slate-900 p-6 space-y-4">
          <h2 className="text-lg font-medium">Deploy version</h2>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Version</label>
            <select
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={selectedVersionId}
              onChange={(e) => setSelectedVersionId(e.target.value)}
            >
              {versions.map((version) => (
                <option key={version.id} value={version.id}>
                  v{version.version_number}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Deployment name</label>
            <Input required value={deploymentName} onChange={(e) => setDeploymentName(e.target.value)} />
          </div>
          <Button type="submit" disabled={isDeploying}>
            {isDeploying ? "Deploying (this may take a minute)..." : "Deploy"}
          </Button>
        </form>
      ) : null}

      <Link to="/models" className="text-sm text-indigo-400 hover:text-indigo-300">
        Back to models
      </Link>
    </section>
  );
}
