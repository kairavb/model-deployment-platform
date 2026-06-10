import logging
from uuid import UUID

from deployment_engine import DeploymentEngineError, IDeploymentEngine

from app.core.exceptions import AppError
from app.modules.deployments.repository import DeploymentRepository
from app.modules.logs.schemas import LogsResponse

logger = logging.getLogger(__name__)


class LogsService:
    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        deployment_engine: IDeploymentEngine,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.deployment_engine = deployment_engine

    async def get_logs(self, user_id: UUID, deployment_id: UUID, tail: int) -> LogsResponse:
        deployment = await self.deployment_repository.get_by_id(deployment_id, user_id)
        if deployment is None:
            raise AppError("Deployment not found.", "DEPLOYMENT_NOT_FOUND", 404)
        if deployment.container_id is None:
            raise AppError("Deployment has no container.", "CONTAINER_NOT_FOUND", 404)

        try:
            logs = await self.deployment_engine.get_logs(deployment.container_id, tail=tail)
        except DeploymentEngineError as exc:
            raise AppError(str(exc), "LOGS_UNAVAILABLE", 404) from exc

        return LogsResponse(
            deployment_id=str(deployment_id),
            tail=tail,
            logs=logs,
        )
