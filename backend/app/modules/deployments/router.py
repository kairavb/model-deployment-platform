from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_current_user_id, get_db, get_deployment_engine
from app.models.deployment import DeploymentStatus
from app.modules.deployments.repository import DeploymentEventRepository, DeploymentRepository
from app.modules.deployments.schemas import (
    DeploymentCreate,
    DeploymentEventResponse,
    DeploymentResponse,
    DeploymentRollback,
    PaginatedDeploymentsResponse,
)
from app.modules.deployments.service import DeploymentService
from app.modules.models.repository import ModelVersionRepository

router = APIRouter(prefix="/deployments")


def get_deployment_service(
    db=Depends(get_db),
    deployment_engine=Depends(get_deployment_engine),
) -> DeploymentService:
    return DeploymentService(
        DeploymentRepository(db),
        DeploymentEventRepository(db),
        ModelVersionRepository(db),
        deployment_engine,
    )


@router.get("", response_model=PaginatedDeploymentsResponse)
async def list_deployments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: DeploymentStatus | None = Query(default=None, alias="status"),
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> PaginatedDeploymentsResponse:
    return await service.list_deployments(user_id, page, page_size, status_filter)


@router.post("", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    payload: DeploymentCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> DeploymentResponse:
    return await service.create_deployment(user_id, payload)


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> DeploymentResponse:
    return await service.get_deployment(user_id, deployment_id)


@router.post("/{deployment_id}/redeploy", response_model=DeploymentResponse)
async def redeploy_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> DeploymentResponse:
    return await service.redeploy_deployment(user_id, deployment_id)


@router.post("/{deployment_id}/rollback", response_model=DeploymentResponse)
async def rollback_deployment(
    deployment_id: UUID,
    payload: DeploymentRollback = DeploymentRollback(),
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> DeploymentResponse:
    return await service.rollback_deployment(user_id, deployment_id, payload)


@router.post("/{deployment_id}/stop", response_model=DeploymentResponse)
async def stop_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> DeploymentResponse:
    return await service.stop_deployment(user_id, deployment_id)


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> None:
    await service.delete_deployment(user_id, deployment_id)


@router.get("/{deployment_id}/health")
async def get_deployment_health(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> dict[str, str]:
    return await service.get_health(user_id, deployment_id)


@router.get("/{deployment_id}/events", response_model=list[DeploymentEventResponse])
async def list_deployment_events(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DeploymentService = Depends(get_deployment_service),
) -> list[DeploymentEventResponse]:
    return await service.list_events(user_id, deployment_id)
