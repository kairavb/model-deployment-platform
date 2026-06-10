import hashlib
import logging
import shutil
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.config import settings
from app.core.exceptions import AppError
from app.models.model import MLModel, ModelFramework
from app.models.model_version import ModelVersion, ModelVersionStatus
from app.modules.deployments.repository import DeploymentRepository
from app.modules.models.repository import ModelRepository, ModelVersionRepository
from app.modules.models.schemas import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    ModelVersionResponse,
    PaginatedModelsResponse,
)
from app.modules.models.validators import validate_model_file

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(
        self,
        model_repository: ModelRepository,
        version_repository: ModelVersionRepository,
        deployment_repository: DeploymentRepository | None = None,
    ) -> None:
        self.model_repository = model_repository
        self.version_repository = version_repository
        self.deployment_repository = deployment_repository

    async def list_models(self, user_id: UUID, page: int, page_size: int) -> PaginatedModelsResponse:
        models, total = await self.model_repository.list_by_user(user_id, page, page_size)
        return PaginatedModelsResponse(
            items=[ModelResponse.model_validate(model) for model in models],
            page=page,
            page_size=page_size,
            total=total,
        )

    async def create_model(self, user_id: UUID, payload: ModelCreate) -> ModelResponse:
        existing = await self.model_repository.get_by_name(user_id, payload.name)
        if existing is not None:
            raise AppError("A model with this name already exists.", "MODEL_NAME_EXISTS", 409)

        model = MLModel(
            user_id=user_id,
            name=payload.name,
            description=payload.description,
            framework=payload.framework,
        )
        created = await self.model_repository.create(model)
        logger.info("Model created: %s by user %s", created.id, user_id)
        return ModelResponse.model_validate(created)

    async def get_model(self, user_id: UUID, model_id: UUID) -> ModelResponse:
        model = await self._get_owned_model(user_id, model_id)
        return ModelResponse.model_validate(model)

    async def update_model(
        self,
        user_id: UUID,
        model_id: UUID,
        payload: ModelUpdate,
    ) -> ModelResponse:
        model = await self._get_owned_model(user_id, model_id)

        if payload.name is not None and payload.name != model.name:
            existing = await self.model_repository.get_by_name(user_id, payload.name)
            if existing is not None:
                raise AppError("A model with this name already exists.", "MODEL_NAME_EXISTS", 409)
            model.name = payload.name

        if payload.description is not None:
            model.description = payload.description

        updated = await self.model_repository.update(model)
        return ModelResponse.model_validate(updated)

    async def delete_model(self, user_id: UUID, model_id: UUID) -> None:
        model = await self._get_owned_model(user_id, model_id)

        if self.deployment_repository is not None:
            running_for_model = await self.deployment_repository.count_active_for_model(model_id)
            if running_for_model > 0:
                raise AppError(
                    "Cannot delete model with active deployments.",
                    "MODEL_HAS_ACTIVE_DEPLOYMENTS",
                    409,
                )

        model_dir = Path(settings.model_storage_path) / str(user_id) / str(model_id)
        await self.model_repository.delete(model)

        if model_dir.exists():
            shutil.rmtree(model_dir, ignore_errors=True)

        logger.info("Model deleted: %s", model_id)

    async def upload_version(
        self,
        user_id: UUID,
        model_id: UUID,
        file: UploadFile,
    ) -> ModelVersionResponse:
        model = await self._get_owned_model(user_id, model_id)

        if file.filename is None:
            raise AppError("Filename is required.", "FILENAME_REQUIRED", 400)

        try:
            suffix = validate_model_file(model.framework, file.filename)
        except ValueError as exc:
            raise AppError(str(exc), "INVALID_FILE_TYPE", 400) from exc

        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        version_number = await self.version_repository.get_next_version_number(model_id)
        version_id = uuid4()

        storage_dir = (
            Path(settings.model_storage_path) / str(user_id) / str(model_id) / f"v{version_number}"
        )
        storage_dir.mkdir(parents=True, exist_ok=True)
        stored_filename = f"model{suffix}"
        file_path = storage_dir / stored_filename

        file_hash, file_size = await self._save_upload(file, file_path, max_bytes)

        version = ModelVersion(
            id=version_id,
            model_id=model_id,
            version_number=version_number,
            file_path=str(file_path.resolve()),
            file_hash=file_hash,
            file_size_bytes=file_size,
            status=ModelVersionStatus.VALIDATED,
        )
        created = await self.version_repository.create(version)
        logger.info("Model version uploaded: %s for model %s", created.id, model_id)
        return ModelVersionResponse.model_validate(created)

    async def list_versions(self, user_id: UUID, model_id: UUID) -> list[ModelVersionResponse]:
        await self._get_owned_model(user_id, model_id)
        versions = await self.version_repository.list_by_model(model_id)
        return [ModelVersionResponse.model_validate(version) for version in versions]

    async def get_version(
        self,
        user_id: UUID,
        model_id: UUID,
        version_id: UUID,
    ) -> ModelVersionResponse:
        await self._get_owned_model(user_id, model_id)
        version = await self.version_repository.get_by_id(version_id, model_id)
        if version is None:
            raise AppError("Model version not found.", "VERSION_NOT_FOUND", 404)
        return ModelVersionResponse.model_validate(version)

    async def delete_version(
        self,
        user_id: UUID,
        model_id: UUID,
        version_id: UUID,
    ) -> None:
        await self._get_owned_model(user_id, model_id)
        version = await self.version_repository.get_by_id(version_id, model_id)
        if version is None:
            raise AppError("Model version not found.", "VERSION_NOT_FOUND", 404)

        if self.deployment_repository is not None:
            active = await self.deployment_repository.count_active_for_version(version_id)
            if active > 0:
                raise AppError(
                    "Cannot delete version with active deployments.",
                    "VERSION_HAS_ACTIVE_DEPLOYMENTS",
                    409,
                )

        file_path = Path(version.file_path)
        await self.version_repository.delete(version)
        if file_path.exists():
            file_path.unlink()

    async def _get_owned_model(self, user_id: UUID, model_id: UUID) -> MLModel:
        model = await self.model_repository.get_by_id(model_id, user_id)
        if model is None:
            raise AppError("Model not found.", "MODEL_NOT_FOUND", 404)
        return model

    async def _save_upload(self, file: UploadFile, destination: Path, max_bytes: int) -> tuple[str, int]:
        hasher = hashlib.sha256()
        size = 0

        with destination.open("wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    destination.unlink(missing_ok=True)
                    raise AppError(
                        f"File exceeds maximum size of {settings.max_upload_size_mb} MB.",
                        "FILE_TOO_LARGE",
                        413,
                    )
                hasher.update(chunk)
                output.write(chunk)

        if size == 0:
            destination.unlink(missing_ok=True)
            raise AppError("Uploaded file is empty.", "EMPTY_FILE", 400)

        return hasher.hexdigest(), size
