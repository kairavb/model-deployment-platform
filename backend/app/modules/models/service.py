from uuid import UUID

from fastapi import UploadFile

from app.modules.models.repository import ModelRepository, ModelVersionRepository
from app.modules.models.schemas import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    ModelVersionResponse,
    PaginatedModelsResponse,
)


class ModelService:
    def __init__(
        self,
        model_repository: ModelRepository,
        version_repository: ModelVersionRepository,
    ) -> None:
        self.model_repository = model_repository
        self.version_repository = version_repository

    async def list_models(self, user_id: UUID, page: int, page_size: int) -> PaginatedModelsResponse:
        raise NotImplementedError("Model listing not implemented yet.")

    async def create_model(self, user_id: UUID, payload: ModelCreate) -> ModelResponse:
        raise NotImplementedError("Model creation not implemented yet.")

    async def get_model(self, user_id: UUID, model_id: UUID) -> ModelResponse:
        raise NotImplementedError("Model retrieval not implemented yet.")

    async def update_model(
        self,
        user_id: UUID,
        model_id: UUID,
        payload: ModelUpdate,
    ) -> ModelResponse:
        raise NotImplementedError("Model update not implemented yet.")

    async def delete_model(self, user_id: UUID, model_id: UUID) -> None:
        raise NotImplementedError("Model deletion not implemented yet.")

    async def upload_version(
        self,
        user_id: UUID,
        model_id: UUID,
        file: UploadFile,
    ) -> ModelVersionResponse:
        raise NotImplementedError("Version upload not implemented yet.")

    async def list_versions(self, user_id: UUID, model_id: UUID) -> list[ModelVersionResponse]:
        raise NotImplementedError("Version listing not implemented yet.")

    async def get_version(
        self,
        user_id: UUID,
        model_id: UUID,
        version_id: UUID,
    ) -> ModelVersionResponse:
        raise NotImplementedError("Version retrieval not implemented yet.")

    async def delete_version(
        self,
        user_id: UUID,
        model_id: UUID,
        version_id: UUID,
    ) -> None:
        raise NotImplementedError("Version deletion not implemented yet.")
