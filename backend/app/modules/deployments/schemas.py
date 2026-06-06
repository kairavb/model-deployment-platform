from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeploymentConfig(BaseModel):
    memory_limit: str = "512m"
    cpu_limit: float = Field(default=1.0, gt=0)


class DeploymentCreate(BaseModel):
    model_version_id: UUID
    name: str = Field(min_length=1, max_length=100)
    config: DeploymentConfig = Field(default_factory=DeploymentConfig)


class DeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_version_id: UUID
    user_id: UUID
    name: str
    status: str
    container_id: str | None
    host_port: int | None
    internal_url: str | None
    health_status: str
    config_json: dict | None
    deployed_at: datetime | None
    stopped_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DeploymentEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    deployment_id: UUID
    event_type: str
    message: str
    metadata_json: dict | None = Field(default=None, validation_alias="metadata")
    created_at: datetime


class PaginatedDeploymentsResponse(BaseModel):
    items: list[DeploymentResponse]
    page: int
    page_size: int
    total: int
