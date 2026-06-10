from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user_id, get_db
from app.modules.deployments.repository import DeploymentRepository
from app.modules.deployments.schemas import InferenceLogResponse
from app.modules.inference.repository import InferenceLogRepository
from app.modules.inference.schemas import PredictRequest, PredictResponse, RawPredictResponse
from app.modules.inference.service import InferenceService

router = APIRouter(prefix="/deployments")


def get_inference_service(db=Depends(get_db)) -> InferenceService:
    return InferenceService(DeploymentRepository(db), InferenceLogRepository(db))


@router.post("/{deployment_id}/predict", response_model=PredictResponse)
async def predict(
    deployment_id: UUID,
    payload: PredictRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: InferenceService = Depends(get_inference_service),
) -> PredictResponse:
    return await service.predict(user_id, deployment_id, payload)


@router.post("/{deployment_id}/predict/raw", response_model=RawPredictResponse)
async def predict_raw(
    deployment_id: UUID,
    body: dict,
    user_id: UUID = Depends(get_current_user_id),
    service: InferenceService = Depends(get_inference_service),
) -> RawPredictResponse:
    return await service.predict_raw(user_id, deployment_id, body)


@router.get("/{deployment_id}/inference-logs", response_model=list[InferenceLogResponse])
async def list_inference_logs(
    deployment_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    user_id: UUID = Depends(get_current_user_id),
    service: InferenceService = Depends(get_inference_service),
) -> list[InferenceLogResponse]:
    logs = await service.list_inference_logs(user_id, deployment_id, limit)
    return [InferenceLogResponse.model_validate(log) for log in logs]
