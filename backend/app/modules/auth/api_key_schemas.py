from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_prefix: str
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class ApiKeyCreatedResponse(ApiKeyResponse):
    key: str
