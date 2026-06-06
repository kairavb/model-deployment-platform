from uuid import UUID

from deployment_engine import IDeploymentEngine

from app.models.deployment import DeploymentStatus
from app.modules.deployments.repository import DeploymentEventRepository, DeploymentRepository
from app.modules.deployments.schemas import (
    DeploymentCreate,
    DeploymentEventResponse,
    DeploymentResponse,
    PaginatedDeploymentsResponse,
)


class DeploymentService:
    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        event_repository: DeploymentEventRepository,
        deployment_engine: IDeploymentEngine,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.event_repository = event_repository
        self.deployment_engine = deployment_engine

    async def list_deployments(
        self,
        user_id: UUID,
        page: int,
        page_size: int,
        status: DeploymentStatus | None = None,
    ) -> PaginatedDeploymentsResponse:
        raise NotImplementedError("Deployment listing not implemented yet.")

    async def create_deployment(
        self,
        user_id: UUID,
        payload: DeploymentCreate,
    ) -> DeploymentResponse:
        raise NotImplementedError("Deployment creation not implemented yet.")

    async def get_deployment(self, user_id: UUID, deployment_id: UUID) -> DeploymentResponse:
        raise NotImplementedError("Deployment retrieval not implemented yet.")

    async def stop_deployment(self, user_id: UUID, deployment_id: UUID) -> DeploymentResponse:
        raise NotImplementedError("Deployment stop not implemented yet.")

    async def delete_deployment(self, user_id: UUID, deployment_id: UUID) -> None:
        raise NotImplementedError("Deployment deletion not implemented yet.")

    async def get_health(self, user_id: UUID, deployment_id: UUID) -> dict[str, str]:
        raise NotImplementedError("Deployment health check not implemented yet.")

    async def list_events(
        self,
        user_id: UUID,
        deployment_id: UUID,
    ) -> list[DeploymentEventResponse]:
        raise NotImplementedError("Deployment event listing not implemented yet.")
