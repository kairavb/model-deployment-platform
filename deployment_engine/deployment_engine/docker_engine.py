import asyncio
import logging
import time
from pathlib import Path

import docker
from docker.errors import APIError, ImageNotFound, NotFound

from deployment_engine.dockerfile_generator import image_tag_for_deployment, prepare_build_context
from deployment_engine.health_checker import HealthChecker
from deployment_engine.models import (
    ContainerHealthStatus,
    ContainerRuntimeStatus,
    ContainerStatus,
    DeploymentResult,
    DeploymentSpec,
)
from deployment_engine.templates import build_container_name

logger = logging.getLogger(__name__)


class DeploymentEngineError(Exception):
    pass


class DockerDeploymentEngine:
    """Builds per-deployment images and manages inference containers via Docker."""

    def __init__(
        self,
        docker_network: str,
        build_base_path: str,
        health_timeout_seconds: int = 60,
        port_min: int = 9000,
        port_max: int = 9999,
        health_checker: HealthChecker | None = None,
    ) -> None:
        self.docker_network = docker_network
        self.build_base_path = Path(build_base_path)
        self.health_timeout_seconds = health_timeout_seconds
        self.port_min = port_min
        self.port_max = port_max
        self.health_checker = health_checker or HealthChecker()
        self._client: docker.DockerClient | None = None

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    async def deploy(self, spec: DeploymentSpec) -> DeploymentResult:
        return await asyncio.to_thread(self._deploy_sync, spec)

    async def stop(self, container_id: str, image_tag: str | None = None) -> None:
        await asyncio.to_thread(self._stop_sync, container_id, image_tag)

    async def get_status(self, container_id: str) -> ContainerStatus:
        return await asyncio.to_thread(self._get_status_sync, container_id)

    async def get_logs(self, container_id: str, tail: int = 100) -> str:
        return await asyncio.to_thread(self._get_logs_sync, container_id, tail)

    async def health_check(self, internal_url: str) -> bool:
        return await self.health_checker.is_healthy(internal_url)

    async def wait_until_healthy(self, internal_url: str) -> bool:
        deadline = time.monotonic() + self.health_timeout_seconds
        while time.monotonic() < deadline:
            if await self.health_checker.is_ready(internal_url):
                return True
            await asyncio.sleep(2)
        return False

    def allocate_port(self, used_ports: set[int]) -> int:
        for port in range(self.port_min, self.port_max + 1):
            if port not in used_ports:
                return port
        raise DeploymentEngineError("No host ports available for deployment")

    def _deploy_sync(self, spec: DeploymentSpec) -> DeploymentResult:
        deployment_id = str(spec.deployment_id)
        container_name = build_container_name(deployment_id)
        build_dir = Path(spec.build_context_path)
        image_tag = spec.image_tag or image_tag_for_deployment(deployment_id)

        logger.info("Preparing build context for deployment %s", deployment_id)
        prepare_build_context(build_dir, spec.model_file_path, spec.framework)

        logger.info("Building image %s", image_tag)
        try:
            self.client.images.build(path=str(build_dir), tag=image_tag, rm=True, pull=True)
        except APIError as exc:
            raise DeploymentEngineError(f"Docker image build failed: {exc}") from exc

        self._remove_existing_container(container_name)

        logger.info("Starting container %s on port %s", container_name, spec.host_port)
        container = None
        try:
            container = self.client.containers.run(
                image=image_tag,
                name=container_name,
                detach=True,
                network=self.docker_network,
                ports={"8080/tcp": spec.host_port},
                mem_limit=spec.memory_limit,
                nano_cpus=int(spec.cpu_limit * 1_000_000_000),
                environment={"MODEL_PATH": "/model/model.file", **spec.env},
                labels={"ai-platform.deployment_id": deployment_id},
            )
        except APIError as exc:
            raise DeploymentEngineError(f"Failed to start container: {exc}") from exc
        except Exception:
            if container is not None:
                container.stop(timeout=5)
                container.remove()
            raise

        internal_url = f"http://{container_name}:8080"
        return DeploymentResult(
            container_id=container.id,
            container_name=container_name,
            host_port=spec.host_port,
            internal_url=internal_url,
            image_tag=image_tag,
        )

    def _stop_sync(self, container_id: str, image_tag: str | None) -> None:
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            container.remove()
            logger.info("Stopped container %s", container_id)
        except NotFound:
            logger.warning("Container %s not found during stop", container_id)

        if image_tag:
            try:
                self.client.images.remove(image_tag, force=True)
                logger.info("Removed image %s", image_tag)
            except ImageNotFound:
                logger.warning("Image %s not found during cleanup", image_tag)

    def _get_status_sync(self, container_id: str) -> ContainerStatus:
        try:
            container = self.client.containers.get(container_id)
            state = container.attrs.get("State", {})
            running = state.get("Running", False)
            ports = container.attrs.get("NetworkSettings", {}).get("Ports", {})
            host_port = None
            for binding in ports.get("8080/tcp", []) or []:
                if binding.get("HostPort"):
                    host_port = int(binding["HostPort"])
                    break

            return ContainerStatus(
                container_id=container_id,
                runtime_status=ContainerRuntimeStatus.RUNNING if running else ContainerRuntimeStatus.STOPPED,
                health_status=ContainerHealthStatus.UNKNOWN,
                host_port=host_port,
                metadata={"status": state.get("Status", "unknown")},
            )
        except NotFound:
            return ContainerStatus(
                container_id=container_id,
                runtime_status=ContainerRuntimeStatus.NOT_FOUND,
                health_status=ContainerHealthStatus.UNKNOWN,
            )

    def _get_logs_sync(self, container_id: str, tail: int) -> str:
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail)
            return logs.decode("utf-8", errors="replace")
        except NotFound as exc:
            raise DeploymentEngineError(f"Container not found: {container_id}") from exc

    def _remove_existing_container(self, container_name: str) -> None:
        try:
            existing = self.client.containers.get(container_name)
            existing.stop(timeout=5)
            existing.remove()
        except NotFound:
            pass
