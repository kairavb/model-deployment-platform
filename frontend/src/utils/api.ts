export function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
}

export function getPredictEndpoint(deploymentId: string): string {
  return `${getApiBaseUrl()}/deployments/${deploymentId}/predict`;
}

export function getDirectEndpoint(hostPort: number | null): string | null {
  if (hostPort === null) {
    return null;
  }
  return `http://localhost:${hostPort}/predict`;
}
