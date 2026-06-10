from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ContainerHealthStatus(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class ContainerRuntimeStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    NOT_FOUND = "not_found"


class DeploymentSpec(BaseModel):
    deployment_id: UUID
    framework: str
    model_file_path: str
    host_port: int
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    env: dict[str, str] = Field(default_factory=dict)
    build_context_path: str
    image_tag: str


class DeploymentResult(BaseModel):
    container_id: str
    container_name: str
    host_port: int
    internal_url: str
    image_tag: str


class ContainerStatus(BaseModel):
    container_id: str
    runtime_status: ContainerRuntimeStatus
    health_status: ContainerHealthStatus
    host_port: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
