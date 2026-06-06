import { apiRequest } from "./client";
import type {
  DeploymentCreate,
  DeploymentEventResponse,
  DeploymentResponse,
  PaginatedDeploymentsResponse,
  PredictRequest,
  PredictResponse,
} from "../types/deployments";

export const deploymentsApi = {
  list(page = 1, pageSize = 20, status?: string) {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    });
    if (status) {
      params.set("status", status);
    }
    return apiRequest<PaginatedDeploymentsResponse>(`/deployments?${params.toString()}`);
  },

  create(payload: DeploymentCreate) {
    return apiRequest<DeploymentResponse>("/deployments", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  get(deploymentId: string) {
    return apiRequest<DeploymentResponse>(`/deployments/${deploymentId}`);
  },

  stop(deploymentId: string) {
    return apiRequest<DeploymentResponse>(`/deployments/${deploymentId}/stop`, {
      method: "POST",
    });
  },

  remove(deploymentId: string) {
    return apiRequest<void>(`/deployments/${deploymentId}`, { method: "DELETE" });
  },

  health(deploymentId: string) {
    return apiRequest<Record<string, string>>(`/deployments/${deploymentId}/health`);
  },

  events(deploymentId: string) {
    return apiRequest<DeploymentEventResponse[]>(`/deployments/${deploymentId}/events`);
  },

  logs(deploymentId: string, tail = 100) {
    return apiRequest<{ logs: string }>(`/deployments/${deploymentId}/logs?tail=${tail}`);
  },

  predict(deploymentId: string, payload: PredictRequest) {
    return apiRequest<PredictResponse>(`/deployments/${deploymentId}/predict`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
