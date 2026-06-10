from uuid import UUID

from fastapi import APIRouter, Depends, Response

from app.dependencies import get_current_user_id, get_db
from app.modules.deployments.repository import DeploymentRepository
from app.modules.deployments.schemas import DeploymentStatsResponse
from app.modules.inference.repository import InferenceLogRepository
from app.modules.monitoring.schemas import HealthResponse, ReadyResponse
from app.modules.monitoring.service import MonitoringService

router = APIRouter()


def get_monitoring_service(db=Depends(get_db)) -> MonitoringService:
    return MonitoringService(DeploymentRepository(db), InferenceLogRepository(db))


@router.get("/health", response_model=HealthResponse)
async def health(service: MonitoringService = Depends(get_monitoring_service)) -> HealthResponse:
    result = await service.get_platform_health()
    return HealthResponse(**result)


@router.get("/ready", response_model=ReadyResponse)
async def ready(service: MonitoringService = Depends(get_monitoring_service)) -> ReadyResponse:
    result = await service.get_platform_ready()
    return ReadyResponse(**result)


@router.get("/deployments/{deployment_id}/metrics")
async def get_deployment_metrics(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: MonitoringService = Depends(get_monitoring_service),
) -> Response:
    metrics = await service.get_deployment_metrics(user_id, deployment_id)
    return Response(content=metrics, media_type="text/plain; version=0.0.4")


@router.get("/deployments/{deployment_id}/stats", response_model=DeploymentStatsResponse)
async def get_deployment_stats(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: MonitoringService = Depends(get_monitoring_service),
) -> DeploymentStatsResponse:
    stats = await service.get_deployment_stats(user_id, deployment_id)
    return DeploymentStatsResponse(**stats)


@router.get("/stats", response_model=DeploymentStatsResponse)
async def get_user_stats(
    user_id: UUID = Depends(get_current_user_id),
    service: MonitoringService = Depends(get_monitoring_service),
) -> DeploymentStatsResponse:
    stats = await service.get_user_stats(user_id)
    return DeploymentStatsResponse(**stats)
