from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user_id, get_db
from app.modules.analytics.schemas import TrendsResponse, UsageResponse
from app.modules.analytics.service import AnalyticsService
from app.modules.inference.repository import InferenceLogRepository

router = APIRouter(prefix="/analytics")


def get_analytics_service(db=Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(InferenceLogRepository(db))


@router.get(
    "/usage",
    response_model=UsageResponse,
    summary="Usage summary",
    description="Request and error totals per deployment for the authenticated user.",
)
async def get_usage(
    user_id: UUID = Depends(get_current_user_id),
    service: AnalyticsService = Depends(get_analytics_service),
) -> UsageResponse:
    return await service.get_usage(user_id)


@router.get(
    "/trends",
    response_model=TrendsResponse,
    summary="Request and error trends",
    description="Daily request and error counts over the selected period.",
)
async def get_trends(
    days: int = Query(default=7, ge=1, le=90),
    user_id: UUID = Depends(get_current_user_id),
    service: AnalyticsService = Depends(get_analytics_service),
) -> TrendsResponse:
    return await service.get_trends(user_id, days)
