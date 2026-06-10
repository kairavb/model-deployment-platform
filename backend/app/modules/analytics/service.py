from uuid import UUID

from app.modules.analytics.schemas import DeploymentUsageItem, TrendsResponse, UsageResponse, TrendPoint
from app.modules.inference.repository import InferenceLogRepository


class AnalyticsService:
    def __init__(self, log_repository: InferenceLogRepository) -> None:
        self.log_repository = log_repository

    async def get_usage(self, user_id: UUID) -> UsageResponse:
        summary = await self.log_repository.get_stats_for_user(user_id)
        by_deployment = await self.log_repository.get_usage_by_deployment(user_id)
        return UsageResponse(
            total_requests=int(summary["request_count"]),
            total_errors=int(summary["error_count"]),
            avg_latency_ms=float(summary["avg_latency_ms"]),
            deployments=[DeploymentUsageItem(**item) for item in by_deployment],
        )

    async def get_trends(self, user_id: UUID, days: int) -> TrendsResponse:
        rows = await self.log_repository.get_daily_trends(user_id, days)
        return TrendsResponse(
            days=days,
            points=[TrendPoint(**row) for row in rows],
        )
