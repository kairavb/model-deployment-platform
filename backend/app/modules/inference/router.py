from uuid import UUID

from deployment_engine import DockerDeploymentEngine
from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_current_user_id, get_db
from app.modules.deployments.repository import DeploymentRepository
from app.modules.inference.schemas import PredictRequest, PredictResponse, RawPredictResponse
from app.modules.inference.service import InferenceService

router = APIRouter(prefix="/deployments")


def get_inference_service(
    db=Depends(get_db),
    deployment_engine: DockerDeploymentEngine = Depends(
        lambda: DockerDeploymentEngine(
            docker_network=settings.docker_network,
            inference_images=settings.inference_images,
        )
    ),
) -> InferenceService:
    return InferenceService(DeploymentRepository(db), deployment_engine)


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
