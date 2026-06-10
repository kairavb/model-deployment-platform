import json
import logging
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.deployment import Deployment, DeploymentStatus

logger = logging.getLogger(__name__)


def _targets_path() -> Path:
    path = Path(settings.prometheus_targets_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


async def sync_inference_targets(session: AsyncSession) -> None:
    """Write Prometheus file_sd targets for running inference containers."""
    result = await session.execute(
        select(Deployment).where(
            Deployment.status == DeploymentStatus.RUNNING,
            Deployment.internal_url.is_not(None),
        )
    )
    deployments = list(result.scalars().all())

    targets: list[dict] = []
    for deployment in deployments:
        assert deployment.internal_url is not None
        host = _host_from_internal_url(deployment.internal_url)
        if host is None:
            continue
        targets.append(
            {
                "targets": [host],
                "labels": {
                    "job": "ai-platform-inference",
                    "deployment_id": str(deployment.id),
                    "deployment_name": deployment.name,
                },
            }
        )

    path = _targets_path()
    path.write_text(json.dumps(targets, indent=2), encoding="utf-8")
    logger.debug("Updated Prometheus targets file with %s inference jobs", len(targets))


def _host_from_internal_url(internal_url: str) -> str | None:
    parsed = urlparse(internal_url)
    if not parsed.hostname:
        return None
    port = parsed.port or 8080
    return f"{parsed.hostname}:{port}"
