export interface DeploymentConfig {
  memory_limit?: string;
  cpu_limit?: number;
}

export interface DeploymentCreate {
  model_version_id: string;
  name: string;
  config?: DeploymentConfig;
}

export interface DeploymentResponse {
  id: string;
  model_version_id: string;
  user_id: string;
  name: string;
  status: string;
  container_id: string | null;
  host_port: number | null;
  internal_url: string | null;
  health_status: string;
  config_json: Record<string, unknown> | null;
  deployed_at: string | null;
  stopped_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeploymentEventResponse {
  id: string;
  deployment_id: string;
  event_type: string;
  message: string;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
}

export interface PaginatedDeploymentsResponse {
  items: DeploymentResponse[];
  page: number;
  page_size: number;
  total: number;
}

export interface PredictRequest {
  inputs: unknown[];
}

export interface PredictResponse {
  outputs: unknown[];
}

export interface InferenceLogResponse {
  id: string;
  deployment_id: string;
  status_code: number;
  latency_ms: number;
  error_message: string | null;
  created_at: string;
}
