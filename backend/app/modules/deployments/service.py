import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from deployment_engine import IDeploymentEngine
from deployment_engine.docker_engine import DeploymentEngineError
from deployment_engine.dockerfile_generator import image_tag_for_deployment
from deployment_engine.models import DeploymentSpec

from app.config import settings
from app.core.exceptions import AppError
from app.core.prometheus_targets import sync_inference_targets
from app.models.deployment import Deployment, DeploymentEvent, DeploymentStatus, HealthStatus
from app.models.model import ModelFramework
from app.models.model_version import ModelVersion
from app.modules.deployments.repository import DeploymentEventRepository, DeploymentRepository
from app.modules.deployments.state_machine import REDEPLOYABLE_STATUSES, ensure_transition
from app.modules.deployments.schemas import (
    DeploymentCreate,
    DeploymentEventResponse,
    DeploymentResponse,
    DeploymentRollback,
    PaginatedDeploymentsResponse,
)
from app.modules.models.repository import ModelVersionRepository

logger = logging.getLogger(__name__)


class DeploymentService:
    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        event_repository: DeploymentEventRepository,
        version_repository: ModelVersionRepository,
        deployment_engine: IDeploymentEngine,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.event_repository = event_repository
        self.version_repository = version_repository
        self.deployment_engine = deployment_engine

    async def list_deployments(
        self,
        user_id: UUID,
        page: int,
        page_size: int,
        status: DeploymentStatus | None = None,
    ) -> PaginatedDeploymentsResponse:
        deployments, total = await self.deployment_repository.list_by_user(
            user_id, page, page_size, status
        )
        return PaginatedDeploymentsResponse(
            items=[self._to_response(deployment) for deployment in deployments],
            page=page,
            page_size=page_size,
            total=total,
        )

    async def create_deployment(
        self,
        user_id: UUID,
        payload: DeploymentCreate,
    ) -> DeploymentResponse:
        active_count = await self.deployment_repository.count_active_by_user(user_id)
        if active_count >= settings.max_deployments_per_user:
            raise AppError(
                f"Maximum of {settings.max_deployments_per_user} active deployments allowed.",
                "DEPLOYMENT_LIMIT_REACHED",
                409,
            )

        version = await self.version_repository.get_by_id_for_user(payload.model_version_id, user_id)
        if version is None:
            raise AppError("Model version not found.", "VERSION_NOT_FOUND", 404)

        model = version.model
        self._validate_version_for_deploy(version, model.framework)

        used_ports = set(await self.deployment_repository.get_allocated_ports())
        host_port = self.deployment_engine.allocate_port(used_ports)

        deployment_id = uuid4()
        image_tag = image_tag_for_deployment(str(deployment_id))
        build_context_path = str(Path(settings.deployment_build_path) / str(deployment_id))

        deployment = Deployment(
            id=deployment_id,
            model_version_id=version.id,
            user_id=user_id,
            name=payload.name,
            status=DeploymentStatus.PENDING,
            host_port=host_port,
            config_json={
                "memory_limit": payload.config.memory_limit,
                "cpu_limit": payload.config.cpu_limit,
                "image_tag": image_tag,
                "build_context_path": build_context_path,
            },
        )
        await self.deployment_repository.create(deployment)
        await self._record_event(deployment.id, "created", "Deployment created")

        await self._start_deployment(deployment, version, model.framework)
        return self._to_response(deployment)

    async def redeploy_deployment(self, user_id: UUID, deployment_id: UUID) -> DeploymentResponse:
        deployment = await self._get_owned_deployment(user_id, deployment_id)
        if deployment.status not in REDEPLOYABLE_STATUSES:
            raise AppError(
                "Deployment cannot be redeployed in its current state.",
                "INVALID_DEPLOYMENT_STATE",
                409,
            )

        version = await self.version_repository.get_by_id_for_user(
            deployment.model_version_id, user_id
        )
        if version is None:
            raise AppError("Model version not found.", "VERSION_NOT_FOUND", 404)

        await self._stop_container_if_needed(deployment)
        await self._record_event(deployment.id, "redeploy", "Redeploying deployment")
        await self._start_deployment(deployment, version, version.model.framework)
        return self._to_response(deployment)

    async def rollback_deployment(
        self,
        user_id: UUID,
        deployment_id: UUID,
        payload: DeploymentRollback,
    ) -> DeploymentResponse:
        deployment = await self._get_owned_deployment(user_id, deployment_id)
        if deployment.status not in REDEPLOYABLE_STATUSES:
            raise AppError(
                "Deployment cannot be rolled back in its current state.",
                "INVALID_DEPLOYMENT_STATE",
                409,
            )

        current_version = await self.version_repository.get_by_id_for_user(
            deployment.model_version_id, user_id
        )
        if current_version is None:
            raise AppError("Model version not found.", "VERSION_NOT_FOUND", 404)

        if payload.model_version_id is not None:
            target = await self.version_repository.get_by_id_for_user(
                payload.model_version_id, user_id
            )
            if target is None or target.model_id != current_version.model_id:
                raise AppError("Target model version not found.", "VERSION_NOT_FOUND", 404)
        else:
            target = await self.version_repository.get_previous_version(
                current_version.model_id,
                current_version.version_number,
            )
            if target is None:
                raise AppError("No previous version to roll back to.", "NO_PREVIOUS_VERSION", 409)

        previous_version_id = str(deployment.model_version_id)
        deployment.model_version_id = target.id
        await self.deployment_repository.save(deployment)
        await self._record_event(
            deployment.id,
            "rollback",
            f"Rolling back to version {target.version_number}",
            {"from_version_id": previous_version_id, "to_version_id": str(target.id)},
        )

        await self._stop_container_if_needed(deployment)
        await self._start_deployment(deployment, target, target.model.framework)
        return self._to_response(deployment)

    async def get_deployment(self, user_id: UUID, deployment_id: UUID) -> DeploymentResponse:
        deployment = await self._get_owned_deployment(user_id, deployment_id)
        return self._to_response(deployment)

    async def stop_deployment(self, user_id: UUID, deployment_id: UUID) -> DeploymentResponse:
        deployment = await self._get_owned_deployment(user_id, deployment_id)
        if deployment.status not in (DeploymentStatus.RUNNING, DeploymentStatus.FAILED):
            raise AppError(
                "Only running or failed deployments can be stopped.",
                "INVALID_DEPLOYMENT_STATE",
                409,
            )

        self._transition(deployment, DeploymentStatus.STOPPING)
        await self.deployment_repository.save(deployment)
        await self._stop_container_if_needed(deployment)

        self._transition(deployment, DeploymentStatus.STOPPED)
        deployment.health_status = HealthStatus.UNKNOWN
        deployment.stopped_at = datetime.now(UTC)
        await self.deployment_repository.save(deployment)
        await self._record_event(deployment.id, "stopped", "Deployment stopped by user")
        await sync_inference_targets(self.deployment_repository.session)
        return self._to_response(deployment)

    async def delete_deployment(self, user_id: UUID, deployment_id: UUID) -> None:
        deployment = await self._get_owned_deployment(user_id, deployment_id)
        if deployment.status == DeploymentStatus.RUNNING:
            await self.stop_deployment(user_id, deployment_id)
            deployment = await self._get_owned_deployment(user_id, deployment_id)
        await self.deployment_repository.delete(deployment)

    async def get_health(self, user_id: UUID, deployment_id: UUID) -> dict[str, str]:
        deployment = await self._get_owned_deployment(user_id, deployment_id)
        if deployment.internal_url is None:
            return {"status": deployment.health_status.value}

        is_healthy = await self.deployment_engine.health_check(deployment.internal_url)
        deployment.health_status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
        await self.deployment_repository.save(deployment)
        return {
            "status": deployment.health_status.value,
            "deployment_status": deployment.status.value,
        }

    async def list_events(
        self,
        user_id: UUID,
        deployment_id: UUID,
    ) -> list[DeploymentEventResponse]:
        await self._get_owned_deployment(user_id, deployment_id)
        events = await self.event_repository.list_by_deployment(deployment_id)
        return [DeploymentEventResponse.model_validate(event) for event in events]

    async def _start_deployment(
        self,
        deployment: Deployment,
        version: ModelVersion,
        framework: ModelFramework,
    ) -> None:
        self._validate_version_for_deploy(version, framework)

        self._transition(deployment, DeploymentStatus.STARTING)
        deployment.health_status = HealthStatus.UNKNOWN
        deployment.stopped_at = None
        await self.deployment_repository.save(deployment)
        await self._record_event(deployment.id, "starting", "Building image and starting container")

        memory_limit = "512m"
        cpu_limit = 1.0
        image_tag = image_tag_for_deployment(str(deployment.id))
        build_context_path = str(Path(settings.deployment_build_path) / str(deployment.id))
        if deployment.config_json:
            memory_limit = deployment.config_json.get("memory_limit", memory_limit)
            cpu_limit = deployment.config_json.get("cpu_limit", cpu_limit)
            image_tag = deployment.config_json.get("image_tag", image_tag)
            build_context_path = deployment.config_json.get("build_context_path", build_context_path)

        assert deployment.host_port is not None

        spec = DeploymentSpec(
            deployment_id=deployment.id,
            framework=framework.value,
            model_file_path=version.file_path,
            host_port=deployment.host_port,
            memory_limit=memory_limit,
            cpu_limit=cpu_limit,
            build_context_path=build_context_path,
            image_tag=image_tag,
        )

        try:
            result = await self.deployment_engine.deploy(spec)
            deployment.container_id = result.container_id
            deployment.internal_url = result.internal_url

            healthy = await self.deployment_engine.wait_until_healthy(result.internal_url)
            if not healthy:
                await self.deployment_engine.stop(result.container_id, image_tag)
                raise DeploymentEngineError("Container failed health check within timeout")

            self._transition(deployment, DeploymentStatus.RUNNING)
            deployment.health_status = HealthStatus.HEALTHY
            deployment.deployed_at = datetime.now(UTC)
            await self.deployment_repository.save(deployment)
            await self._record_event(
                deployment.id,
                "healthy",
                "Deployment is running",
                {"host_port": deployment.host_port, "internal_url": result.internal_url},
            )
            logger.info("Deployment %s is running on port %s", deployment.id, deployment.host_port)
            await sync_inference_targets(self.deployment_repository.session)
        except (DeploymentEngineError, Exception) as exc:
            logger.exception("Deployment %s failed", deployment.id)
            self._transition(deployment, DeploymentStatus.FAILED)
            deployment.health_status = HealthStatus.UNHEALTHY
            deployment.stopped_at = datetime.now(UTC)
            await self._stop_container_if_needed(deployment)
            await self.deployment_repository.save(deployment)
            await self._record_event(deployment.id, "failed", str(exc))
            await sync_inference_targets(self.deployment_repository.session)
            raise AppError(
                f"Deployment failed: {exc}",
                "DEPLOYMENT_FAILED",
                500,
                hint="Check deployment logs and ensure Docker has enough resources.",
            ) from exc

    async def _stop_container_if_needed(self, deployment: Deployment) -> None:
        if not deployment.container_id:
            return
        image_tag = deployment.config_json.get("image_tag") if deployment.config_json else None
        try:
            await self.deployment_engine.stop(deployment.container_id, image_tag)
        except Exception:
            logger.warning("Failed to stop container for deployment %s", deployment.id)

    def _validate_version_for_deploy(self, version: ModelVersion, framework: ModelFramework) -> None:
        if framework != ModelFramework.SKLEARN:
            raise AppError(
                "Only sklearn models can be deployed at this time.",
                "UNSUPPORTED_FRAMEWORK",
                400,
            )
        if not Path(version.file_path).is_file():
            raise AppError("Model file is missing on disk.", "MODEL_FILE_MISSING", 400)

    async def _get_owned_deployment(self, user_id: UUID, deployment_id: UUID) -> Deployment:
        deployment = await self.deployment_repository.get_by_id(deployment_id, user_id)
        if deployment is None:
            raise AppError("Deployment not found.", "DEPLOYMENT_NOT_FOUND", 404)
        return deployment

    async def _record_event(
        self,
        deployment_id: UUID,
        event_type: str,
        message: str,
        metadata: dict | None = None,
    ) -> None:
        await self.event_repository.create(
            DeploymentEvent(
                deployment_id=deployment_id,
                event_type=event_type,
                message=message,
                metadata_json=metadata,
            )
        )

    def _transition(self, deployment: Deployment, next_status: DeploymentStatus) -> None:
        ensure_transition(deployment.status, next_status)
        deployment.status = next_status

    def _to_response(self, deployment: Deployment) -> DeploymentResponse:
        return DeploymentResponse.model_validate(deployment)
