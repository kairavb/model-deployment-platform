import logging

import httpx

logger = logging.getLogger(__name__)


class HealthChecker:
    """Performs HTTP health checks against inference containers."""

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.timeout_seconds = timeout_seconds

    async def _get_status(self, url: str) -> int | None:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url)
                return response.status_code
        except httpx.HTTPError as exc:
            logger.debug("Health probe failed for %s: %s", url, exc)
            return None

    async def is_healthy(self, internal_url: str) -> bool:
        status = await self._get_status(f"{internal_url.rstrip('/')}/health")
        return status == 200

    async def is_ready(self, internal_url: str) -> bool:
        status = await self._get_status(f"{internal_url.rstrip('/')}/ready")
        return status == 200
