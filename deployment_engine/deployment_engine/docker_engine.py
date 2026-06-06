from deployment_engine.health_checker import HealthChecker
from deployment_engine.interface import IDeploymentEngine
from deployment_engine.models import (
    ContainerHealthStatus,
    ContainerRuntimeStatus,
    ContainerStatus,
    DeploymentResult,
    DeploymentSpec,
)


class DockerDeploymentEngine:
    """Docker SDK implementation of the deployment engine."""

    def __init__(
        self,
        docker_network: str,
        inference_images: dict[str, str],
        health_checker: HealthChecker | None = None,
    ) -> None:
        self.docker_network = docker_network
        self.inference_images = inference_images
        self.health_checker = health_checker or HealthChecker()

    async def deploy(self, spec: DeploymentSpec) -> DeploymentResult:
        raise NotImplementedError("Deployment logic not implemented yet.")

    async def stop(self, container_id: str) -> None:
        raise NotImplementedError("Stop logic not implemented yet.")

    async def get_status(self, container_id: str) -> ContainerStatus:
        return ContainerStatus(
            container_id=container_id,
            runtime_status=ContainerRuntimeStatus.NOT_FOUND,
            health_status=ContainerHealthStatus.UNKNOWN,
        )

    async def get_logs(self, container_id: str, tail: int = 100) -> str:
        raise NotImplementedError("Log retrieval not implemented yet.")

    async def health_check(self, internal_url: str) -> bool:
        return await self.health_checker.is_healthy(internal_url)
