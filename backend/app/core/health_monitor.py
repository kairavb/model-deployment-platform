import asyncio
import logging
from sqlalchemy import select

from app.core.prometheus_targets import sync_inference_targets
from app.db.session import SessionLocal
from app.models.deployment import Deployment, DeploymentStatus, HealthStatus
from app.modules.deployments.repository import DeploymentRepository

logger = logging.getLogger(__name__)

MONITOR_INTERVAL_SECONDS = 30


async def run_health_monitor(get_engine) -> None:
    """Periodically probe running deployments and update health_status."""
    while True:
        try:
            await _check_all_deployments(get_engine)
        except Exception:
            logger.exception("Health monitor iteration failed")
        await asyncio.sleep(MONITOR_INTERVAL_SECONDS)


async def _check_all_deployments(get_engine) -> None:
    engine = get_engine()
    async with SessionLocal() as session:
        result = await session.execute(
            select(Deployment).where(
                Deployment.status == DeploymentStatus.RUNNING,
                Deployment.internal_url.is_not(None),
            )
        )
        deployments = list(result.scalars().all())
        await sync_inference_targets(session)

        if not deployments:
            return

        repository = DeploymentRepository(session)
        for deployment in deployments:
            assert deployment.internal_url is not None
            is_healthy = await engine.health_check(deployment.internal_url)
            new_status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
            if deployment.health_status != new_status:
                deployment.health_status = new_status
                await repository.save(deployment)
                logger.info(
                    "Deployment %s health updated to %s",
                    deployment.id,
                    new_status.value,
                )
