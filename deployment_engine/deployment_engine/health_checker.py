import httpx


class HealthChecker:
    """Performs HTTP health checks against inference containers."""

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.timeout_seconds = timeout_seconds

    async def is_healthy(self, internal_url: str) -> bool:
        """Return True when the /health endpoint responds with HTTP 200."""
        health_url = f"{internal_url.rstrip('/')}/health"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(health_url)
            return response.status_code == 200
