from typing import Protocol

from deployment_engine.models import ContainerStatus, DeploymentResult, DeploymentSpec


class IDeploymentEngine(Protocol):
    """Contract for deploying and managing inference containers."""

    async def deploy(self, spec: DeploymentSpec) -> DeploymentResult:
        ...

    async def stop(self, container_id: str, image_tag: str | None = None) -> None:
        ...

    async def get_status(self, container_id: str) -> ContainerStatus:
        ...

    async def get_logs(self, container_id: str, tail: int = 100) -> str:
        ...

    async def health_check(self, internal_url: str) -> bool:
        ...

    async def wait_until_healthy(self, internal_url: str) -> bool:
        ...

    def allocate_port(self, used_ports: set[int]) -> int:
        ...
