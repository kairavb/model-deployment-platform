import { apiRequest } from "./client";

export interface DeploymentUsageItem {
  deployment_id: string;
  deployment_name: string;
  request_count: number;
  error_count: number;
  avg_latency_ms: number;
}

export interface UsageResponse {
  total_requests: number;
  total_errors: number;
  avg_latency_ms: number;
  deployments: DeploymentUsageItem[];
}

export interface TrendPoint {
  date: string;
  request_count: number;
  error_count: number;
}

export interface TrendsResponse {
  days: number;
  points: TrendPoint[];
}

export const analyticsApi = {
  usage() {
    return apiRequest<UsageResponse>("/analytics/usage");
  },

  trends(days = 7) {
    return apiRequest<TrendsResponse>(`/analytics/trends?days=${days}`);
  },
};
