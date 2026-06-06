from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.dependencies import get_current_user_id, get_db
from app.modules.models.repository import ModelRepository, ModelVersionRepository
from app.modules.models.schemas import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    ModelVersionResponse,
    PaginatedModelsResponse,
)
from app.modules.models.service import ModelService

router = APIRouter(prefix="/models")


def get_model_service(db=Depends(get_db)) -> ModelService:
    return ModelService(ModelRepository(db), ModelVersionRepository(db))


@router.get("", response_model=PaginatedModelsResponse)
async def list_models(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> PaginatedModelsResponse:
    return await service.list_models(user_id, page, page_size)


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    payload: ModelCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    return await service.create_model(user_id, payload)


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    return await service.get_model(user_id, model_id)


@router.patch("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: UUID,
    payload: ModelUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    return await service.update_model(user_id, model_id, payload)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> None:
    await service.delete_model(user_id, model_id)


@router.post("/{model_id}/versions", response_model=ModelVersionResponse, status_code=status.HTTP_201_CREATED)
async def upload_version(
    model_id: UUID,
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> ModelVersionResponse:
    return await service.upload_version(user_id, model_id, file)


@router.get("/{model_id}/versions", response_model=list[ModelVersionResponse])
async def list_versions(
    model_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> list[ModelVersionResponse]:
    return await service.list_versions(user_id, model_id)


@router.get("/{model_id}/versions/{version_id}", response_model=ModelVersionResponse)
async def get_version(
    model_id: UUID,
    version_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> ModelVersionResponse:
    return await service.get_version(user_id, model_id, version_id)


@router.delete("/{model_id}/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(
    model_id: UUID,
    version_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service),
) -> None:
    await service.delete_version(user_id, model_id, version_id)
