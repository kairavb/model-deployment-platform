from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deployment import Deployment
from app.models.inference_log import InferenceLog


class InferenceLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, log: InferenceLog) -> InferenceLog:
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log

    async def list_by_deployment(self, deployment_id: UUID, limit: int) -> list[InferenceLog]:
        result = await self.session.execute(
            select(InferenceLog)
            .where(InferenceLog.deployment_id == deployment_id)
            .order_by(InferenceLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(self, deployment_id: UUID) -> dict[str, float | int]:
        result = await self.session.execute(
            select(
                func.count(InferenceLog.id),
                func.count(InferenceLog.id).filter(InferenceLog.status_code >= 400),
                func.coalesce(func.avg(InferenceLog.latency_ms), 0.0),
            ).where(InferenceLog.deployment_id == deployment_id)
        )
        request_count, error_count, avg_latency = result.one()
        return {
            "request_count": int(request_count),
            "error_count": int(error_count),
            "avg_latency_ms": round(float(avg_latency), 2),
        }

    async def get_stats_for_user(self, user_id: UUID) -> dict[str, float | int]:
        result = await self.session.execute(
            select(
                func.count(InferenceLog.id),
                func.count(InferenceLog.id).filter(InferenceLog.status_code >= 400),
                func.coalesce(func.avg(InferenceLog.latency_ms), 0.0),
            )
            .select_from(InferenceLog)
            .join(Deployment, InferenceLog.deployment_id == Deployment.id)
            .where(Deployment.user_id == user_id)
        )
        request_count, error_count, avg_latency = result.one()
        return {
            "request_count": int(request_count),
            "error_count": int(error_count),
            "avg_latency_ms": round(float(avg_latency), 2),
        }

    async def get_usage_by_deployment(self, user_id: UUID) -> list[dict]:
        result = await self.session.execute(
            select(
                Deployment.id,
                Deployment.name,
                func.count(InferenceLog.id),
                func.count(InferenceLog.id).filter(InferenceLog.status_code >= 400),
                func.coalesce(func.avg(InferenceLog.latency_ms), 0.0),
            )
            .outerjoin(InferenceLog, InferenceLog.deployment_id == Deployment.id)
            .where(Deployment.user_id == user_id)
            .group_by(Deployment.id, Deployment.name)
            .order_by(func.count(InferenceLog.id).desc())
        )
        return [
            {
                "deployment_id": row[0],
                "deployment_name": row[1],
                "request_count": int(row[2]),
                "error_count": int(row[3]),
                "avg_latency_ms": round(float(row[4]), 2),
            }
            for row in result.all()
        ]

    async def get_daily_trends(self, user_id: UUID, days: int) -> list[dict]:
        since = datetime.now(UTC) - timedelta(days=days)
        day_bucket = func.date_trunc("day", InferenceLog.created_at).label("day")
        result = await self.session.execute(
            select(
                day_bucket,
                func.count(InferenceLog.id),
                func.count(InferenceLog.id).filter(InferenceLog.status_code >= 400),
            )
            .select_from(InferenceLog)
            .join(Deployment, InferenceLog.deployment_id == Deployment.id)
            .where(Deployment.user_id == user_id, InferenceLog.created_at >= since)
            .group_by(day_bucket)
            .order_by(day_bucket)
        )
        points: list[dict] = []
        for row in result.all():
            day_value = row[0]
            if hasattr(day_value, "date"):
                day_value = day_value.date()
            points.append(
                {
                    "date": day_value,
                    "request_count": int(row[1]),
                    "error_count": int(row[2]),
                }
            )
        return points
