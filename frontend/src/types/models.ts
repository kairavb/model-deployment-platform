export type ModelFramework = "sklearn" | "onnx" | "pytorch";

export interface ModelCreate {
  name: string;
  description?: string;
  framework: ModelFramework;
}

export interface ModelUpdate {
  name?: string;
  description?: string;
}

export interface ModelResponse {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  framework: ModelFramework;
  created_at: string;
  updated_at: string;
}

export interface ModelVersionResponse {
  id: string;
  model_id: string;
  version_number: number;
  file_path: string;
  file_hash: string;
  file_size_bytes: number;
  input_schema_json: Record<string, unknown> | null;
  output_schema_json: Record<string, unknown> | null;
  status: string;
  created_at: string;
}

export interface PaginatedModelsResponse {
  items: ModelResponse[];
  page: number;
  page_size: number;
  total: number;
}
