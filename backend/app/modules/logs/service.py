from uuid import UUID

from deployment_engine import IDeploymentEngine

from app.modules.deployments.repository import DeploymentRepository
from app.modules.logs.schemas import LogsResponse


class LogsService:
    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        deployment_engine: IDeploymentEngine,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.deployment_engine = deployment_engine

    async def get_logs(self, user_id: UUID, deployment_id: UUID, tail: int) -> LogsResponse:
        raise NotImplementedError("Log retrieval not implemented yet.")
