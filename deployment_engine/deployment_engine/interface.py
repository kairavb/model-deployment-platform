from typing import Protocol

from deployment_engine.models import ContainerStatus, DeploymentResult, DeploymentSpec


class IDeploymentEngine(Protocol):
    """Contract for deploying and managing inference containers."""

    async def deploy(self, spec: DeploymentSpec) -> DeploymentResult:
        """Start an inference container for the given deployment spec."""
        ...

    async def stop(self, container_id: str) -> None:
        """Stop and remove an inference container."""
        ...

    async def get_status(self, container_id: str) -> ContainerStatus:
        """Return runtime status for a container."""
        ...

    async def get_logs(self, container_id: str, tail: int = 100) -> str:
        """Return recent container logs."""
        ...

    async def health_check(self, internal_url: str) -> bool:
        """Return True when the inference service responds healthy."""
        ...
