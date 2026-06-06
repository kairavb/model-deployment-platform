from uuid import UUID

from deployment_engine import DockerDeploymentEngine
from fastapi import APIRouter, Depends, Query

from app.config import settings
from app.dependencies import get_current_user_id, get_db
from app.modules.deployments.repository import DeploymentRepository
from app.modules.logs.schemas import LogsResponse
from app.modules.logs.service import LogsService

router = APIRouter(prefix="/deployments")


def get_logs_service(
    db=Depends(get_db),
    deployment_engine: DockerDeploymentEngine = Depends(
        lambda: DockerDeploymentEngine(
            docker_network=settings.docker_network,
            inference_images=settings.inference_images,
        )
    ),
) -> LogsService:
    return LogsService(DeploymentRepository(db), deployment_engine)


@router.get("/{deployment_id}/logs", response_model=LogsResponse)
async def get_deployment_logs(
    deployment_id: UUID,
    tail: int = Query(default=100, ge=1, le=1000),
    user_id: UUID = Depends(get_current_user_id),
    service: LogsService = Depends(get_logs_service),
) -> LogsResponse:
    return await service.get_logs(user_id, deployment_id, tail)
