import { getApiBaseUrl } from "../utils/api";
import { getAuthToken } from "../utils/authToken";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public hint?: string,
    public requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers);

  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as {
      detail?: string;
      code?: string;
      hint?: string;
      request_id?: string;
    };
    throw new ApiError(
      errorBody.detail ?? "Request failed",
      response.status,
      errorBody.code,
      errorBody.hint,
      errorBody.request_id,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
