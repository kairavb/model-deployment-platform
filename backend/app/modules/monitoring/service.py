from uuid import UUID

from app.modules.deployments.repository import DeploymentRepository


class MonitoringService:
    def __init__(self, deployment_repository: DeploymentRepository) -> None:
        self.deployment_repository = deployment_repository

    async def get_platform_health(self) -> dict[str, str]:
        return {"status": "ok"}

    async def get_platform_ready(self) -> dict[str, str]:
        raise NotImplementedError("Readiness check not implemented yet.")

    async def get_deployment_metrics(self, user_id: UUID, deployment_id: UUID) -> str:
        raise NotImplementedError("Deployment metrics not implemented yet.")
