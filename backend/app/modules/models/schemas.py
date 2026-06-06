from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.model import ModelFramework


class ModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    framework: ModelFramework


class ModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    framework: ModelFramework
    created_at: datetime
    updated_at: datetime


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_id: UUID
    version_number: int
    file_path: str
    file_hash: str
    file_size_bytes: int
    input_schema_json: dict | None
    output_schema_json: dict | None
    status: str
    created_at: datetime


class PaginatedModelsResponse(BaseModel):
    items: list[ModelResponse]
    page: int
    page_size: int
    total: int
