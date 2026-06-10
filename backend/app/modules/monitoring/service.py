import logging
from uuid import UUID

import docker
import httpx
from sqlalchemy import text

from app.core.exceptions import AppError
from app.models.deployment import DeploymentStatus
from app.modules.deployments.repository import DeploymentRepository
from app.modules.inference.repository import InferenceLogRepository

logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        log_repository: InferenceLogRepository,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.log_repository = log_repository

    async def get_platform_health(self) -> dict[str, str]:
        return {"status": "ok"}

    async def get_platform_ready(self) -> dict[str, str]:
        database_status = "ok"
        docker_status = "ok"

        try:
            from app.db.session import engine

            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception as exc:
            logger.error("Database readiness check failed: %s", exc)
            database_status = "error"

        try:
            client = docker.from_env()
            client.ping()
        except Exception as exc:
            logger.error("Docker readiness check failed: %s", exc)
            docker_status = "error"

        overall = "ok" if database_status == "ok" and docker_status == "ok" else "degraded"
        return {
            "status": overall,
            "database": database_status,
            "docker": docker_status,
        }

    async def get_deployment_metrics(self, user_id: UUID, deployment_id: UUID) -> str:
        deployment = await self.deployment_repository.get_by_id(deployment_id, user_id)
        if deployment is None:
            raise AppError("Deployment not found.", "DEPLOYMENT_NOT_FOUND", 404)
        if deployment.status != DeploymentStatus.RUNNING or deployment.internal_url is None:
            raise AppError("Deployment is not running.", "DEPLOYMENT_NOT_RUNNING", 409)

        metrics_url = f"{deployment.internal_url.rstrip('/')}/metrics"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(metrics_url)
            response.raise_for_status()
            return response.text

    async def get_deployment_stats(self, user_id: UUID, deployment_id: UUID) -> dict[str, float | int]:
        deployment = await self.deployment_repository.get_by_id(deployment_id, user_id)
        if deployment is None:
            raise AppError("Deployment not found.", "DEPLOYMENT_NOT_FOUND", 404)
        return await self.log_repository.get_stats(deployment_id)

    async def get_user_stats(self, user_id: UUID) -> dict[str, float | int]:
        return await self.log_repository.get_stats_for_user(user_id)
