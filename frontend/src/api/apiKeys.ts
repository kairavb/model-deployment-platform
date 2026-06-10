import { apiRequest } from "./client";

export interface ApiKeyResponse {
  id: string;
  name: string;
  key_prefix: string;
  last_used_at: string | null;
  revoked_at: string | null;
  created_at: string;
}

export interface ApiKeyCreatedResponse extends ApiKeyResponse {
  key: string;
}

export const apiKeysApi = {
  list() {
    return apiRequest<ApiKeyResponse[]>("/auth/api-keys");
  },

  create(name: string) {
    return apiRequest<ApiKeyCreatedResponse>("/auth/api-keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  },

  revoke(keyId: string) {
    return apiRequest<void>(`/auth/api-keys/${keyId}`, { method: "DELETE" });
  },
};
