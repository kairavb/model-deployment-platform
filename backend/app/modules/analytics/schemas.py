from datetime import date
from uuid import UUID

from pydantic import BaseModel


class DeploymentUsageItem(BaseModel):
    deployment_id: UUID
    deployment_name: str
    request_count: int
    error_count: int
    avg_latency_ms: float


class UsageResponse(BaseModel):
    total_requests: int
    total_errors: int
    avg_latency_ms: float
    deployments: list[DeploymentUsageItem]


class TrendPoint(BaseModel):
    date: date
    request_count: int
    error_count: int


class TrendsResponse(BaseModel):
    days: int
    points: list[TrendPoint]
