import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { modelsApi } from "../api/models";
import { ApiError } from "../api/client";
import { PageHeader } from "../components/shared/PageHeader";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import type { ModelFramework, ModelResponse } from "../types/models";
import { formatDate } from "../utils/format";

export function ModelsPage() {
  const [models, setModels] = useState<ModelResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [framework, setFramework] = useState<ModelFramework>("sklearn");
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  async function loadModels() {
    setIsLoading(true);
    setError(null);
    try {
      const response = await modelsApi.list();
      setModels(response.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load models");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadModels();
  }, []);

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setUploadError("Please select a model file.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const model = await modelsApi.create({ name, description: description || undefined, framework });
      const uploadResponse = await modelsApi.uploadVersion(model.id, file);
      if (!uploadResponse.ok) {
        const body = (await uploadResponse.json()) as { detail?: string };
        throw new ApiError(body.detail ?? "Upload failed", uploadResponse.status);
      }
      setName("");
      setDescription("");
      setFile(null);
      await loadModels();
    } catch (err) {
      setUploadError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(modelId: string) {
    if (!window.confirm("Delete this model and all versions?")) {
      return;
    }
    try {
      await modelsApi.remove(modelId);
      await loadModels();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete model");
    }
  }

  return (
    <section className="space-y-8">
      <PageHeader title="Models" description="Upload sklearn models and manage versions." />

      <form
        onSubmit={handleUpload}
        className="rounded-lg border border-slate-800 bg-slate-900 p-6 space-y-4"
      >
        <h2 className="text-lg font-medium">Upload model</h2>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm text-slate-400">Name</label>
            <Input required value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Framework</label>
            <select
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={framework}
              onChange={(e) => setFramework(e.target.value as ModelFramework)}
            >
              <option value="sklearn">sklearn (.pkl, .joblib)</option>
              <option value="onnx" disabled>
                onnx (coming soon)
              </option>
              <option value="pytorch" disabled>
                pytorch (coming soon)
              </option>
            </select>
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm text-slate-400">Description</label>
          <Input value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>

        <div>
          <label className="mb-1 block text-sm text-slate-400">Model file</label>
          <Input
            type="file"
            accept=".pkl,.joblib"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>

        {uploadError ? <p className="text-sm text-rose-400">{uploadError}</p> : null}

        <Button type="submit" disabled={isUploading}>
          {isUploading ? "Uploading..." : "Upload model"}
        </Button>
      </form>

      <div className="rounded-lg border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 px-6 py-4">
          <h2 className="text-lg font-medium">Your models</h2>
        </div>

        {isLoading ? <p className="p-6 text-sm text-slate-400">Loading models...</p> : null}
        {error ? <p className="p-6 text-sm text-rose-400">{error}</p> : null}

        {!isLoading && models.length === 0 ? (
          <p className="p-6 text-sm text-slate-400">No models yet. Upload your first model above.</p>
        ) : null}

        {!isLoading && models.length > 0 ? (
          <div className="divide-y divide-slate-800">
            {models.map((model) => (
              <div key={model.id} className="flex items-center justify-between px-6 py-4">
                <div>
                  <Link to={`/models/${model.id}`} className="font-medium text-indigo-400 hover:text-indigo-300">
                    {model.name}
                  </Link>
                  <p className="text-sm text-slate-400">
                    {model.framework} · Created {formatDate(model.created_at)}
                  </p>
                </div>
                <Button type="button" onClick={() => void handleDelete(model.id)} className="!bg-rose-700 hover:!bg-rose-600">
                  Delete
                </Button>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}
