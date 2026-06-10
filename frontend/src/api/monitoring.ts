import { apiRequest } from "./client";

export interface DeploymentStats {
  request_count: number;
  error_count: number;
  avg_latency_ms: number;
}

export const monitoringApi = {
  userStats() {
    return apiRequest<DeploymentStats>("/stats");
  },

  deploymentStats(deploymentId: string) {
    return apiRequest<DeploymentStats>(`/deployments/${deploymentId}/stats`);
  },
};
