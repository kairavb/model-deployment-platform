from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user_id, get_db, get_deployment_engine
from app.modules.deployments.repository import DeploymentRepository
from app.modules.logs.schemas import LogsResponse
from app.modules.logs.service import LogsService

router = APIRouter(prefix="/deployments")


def get_logs_service(
    db=Depends(get_db),
    deployment_engine=Depends(get_deployment_engine),
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
