import { FormEvent, useEffect, useState } from "react";

import { apiKeysApi, type ApiKeyCreatedResponse, type ApiKeyResponse } from "../api/apiKeys";
import { ApiError } from "../api/client";
import { PageHeader } from "../components/shared/PageHeader";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { formatDate } from "../utils/format";

export function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKeyResponse[]>([]);
  const [name, setName] = useState("");
  const [newKey, setNewKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  async function loadKeys() {
    try {
      const response = await apiKeysApi.list();
      setKeys(response);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load API keys");
    }
  }

  useEffect(() => {
    void loadKeys();
  }, []);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) {
      return;
    }
    setIsCreating(true);
    setError(null);
    try {
      const created: ApiKeyCreatedResponse = await apiKeysApi.create(name.trim());
      setNewKey(created.key);
      setName("");
      await loadKeys();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create API key");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleRevoke(keyId: string) {
    setError(null);
    try {
      await apiKeysApi.revoke(keyId);
      await loadKeys();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to revoke API key");
    }
  }

  return (
    <section className="space-y-8">
      <PageHeader
        title="API Keys"
        description="Generate keys for programmatic access to the platform API."
      />

      {error ? <p className="text-sm text-rose-400">{error}</p> : null}

      {newKey ? (
        <div className="rounded-lg border border-amber-800/50 bg-amber-950/30 p-4 text-sm">
          <p className="mb-2 font-medium text-amber-200">Copy your new API key now — it won&apos;t be shown again.</p>
          <code className="block overflow-x-auto rounded bg-slate-950 px-3 py-2 text-xs">{newKey}</code>
          <Button type="button" className="mt-3" onClick={() => void navigator.clipboard.writeText(newKey)}>
            Copy key
          </Button>
        </div>
      ) : null}

      <form onSubmit={handleCreate} className="flex max-w-md gap-3">
        <Input
          placeholder="Key name (e.g. production)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <Button type="submit" disabled={isCreating}>
          {isCreating ? "Creating..." : "Generate"}
        </Button>
      </form>

      <div className="rounded-lg border border-slate-800 bg-slate-900">
        {keys.length === 0 ? (
          <p className="p-6 text-sm text-slate-400">No API keys yet.</p>
        ) : (
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-slate-800 text-slate-400">
              <tr>
                <th className="px-6 py-3 font-medium">Name</th>
                <th className="px-6 py-3 font-medium">Prefix</th>
                <th className="px-6 py-3 font-medium">Created</th>
                <th className="px-6 py-3 font-medium">Last used</th>
                <th className="px-6 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {keys.map((key) => (
                <tr key={key.id}>
                  <td className="px-6 py-4">{key.name}</td>
                  <td className="px-6 py-4 font-mono text-slate-400">{key.key_prefix}…</td>
                  <td className="px-6 py-4 text-slate-400">{formatDate(key.created_at)}</td>
                  <td className="px-6 py-4 text-slate-400">
                    {key.last_used_at ? formatDate(key.last_used_at) : "Never"}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button
                      type="button"
                      onClick={() => void handleRevoke(key.id)}
                      className="!bg-rose-700 hover:!bg-rose-600 !px-3 !py-1.5"
                    >
                      Revoke
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
