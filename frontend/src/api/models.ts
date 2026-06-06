import { apiRequest } from "./client";
import type {
  ModelCreate,
  ModelResponse,
  ModelUpdate,
  ModelVersionResponse,
  PaginatedModelsResponse,
} from "../types/models";

export const modelsApi = {
  list(page = 1, pageSize = 20) {
    return apiRequest<PaginatedModelsResponse>(`/models?page=${page}&page_size=${pageSize}`);
  },

  create(payload: ModelCreate) {
    return apiRequest<ModelResponse>("/models", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  get(modelId: string) {
    return apiRequest<ModelResponse>(`/models/${modelId}`);
  },

  update(modelId: string, payload: ModelUpdate) {
    return apiRequest<ModelResponse>(`/models/${modelId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  remove(modelId: string) {
    return apiRequest<void>(`/models/${modelId}`, { method: "DELETE" });
  },

  listVersions(modelId: string) {
    return apiRequest<ModelVersionResponse[]>(`/models/${modelId}/versions`);
  },

  uploadVersion(modelId: string, file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const token = localStorage.getItem("access_token");
    return fetch(`${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1"}/models/${modelId}/versions`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      body: formData,
    });
  },
};
