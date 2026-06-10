from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.model import MLModel
from app.models.model_version import ModelVersion


class ModelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_user(self, user_id: UUID, page: int, page_size: int) -> tuple[list[MLModel], int]:
        query = (
            select(MLModel)
            .where(MLModel.user_id == user_id)
            .order_by(MLModel.created_at.desc())
            .options(selectinload(MLModel.versions))
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(MLModel).where(MLModel.user_id == user_id)
        )
        total = total_result.scalar_one()
        result = await self.session.execute(query.offset((page - 1) * page_size).limit(page_size))
        return list(result.scalars().unique().all()), total

    async def get_by_id(self, model_id: UUID, user_id: UUID) -> MLModel | None:
        result = await self.session.execute(
            select(MLModel)
            .where(MLModel.id == model_id, MLModel.user_id == user_id)
            .options(selectinload(MLModel.versions))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, user_id: UUID, name: str) -> MLModel | None:
        result = await self.session.execute(
            select(MLModel).where(MLModel.user_id == user_id, MLModel.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, model: MLModel) -> MLModel:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def update(self, model: MLModel) -> MLModel:
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete(self, model: MLModel) -> None:
        self.session.delete(model)
        await self.session.commit()


class ModelVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_model(self, model_id: UUID) -> list[ModelVersion]:
        result = await self.session.execute(
            select(ModelVersion)
            .where(ModelVersion.model_id == model_id)
            .order_by(ModelVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, version_id: UUID, model_id: UUID) -> ModelVersion | None:
        result = await self.session.execute(
            select(ModelVersion).where(
                ModelVersion.id == version_id,
                ModelVersion.model_id == model_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, version_id: UUID, user_id: UUID) -> ModelVersion | None:
        result = await self.session.execute(
            select(ModelVersion)
            .join(MLModel, ModelVersion.model_id == MLModel.id)
            .where(ModelVersion.id == version_id, MLModel.user_id == user_id)
            .options(selectinload(ModelVersion.model))
        )
        return result.scalar_one_or_none()

    async def get_previous_version(
        self, model_id: UUID, current_version_number: int
    ) -> ModelVersion | None:
        result = await self.session.execute(
            select(ModelVersion)
            .where(
                ModelVersion.model_id == model_id,
                ModelVersion.version_number < current_version_number,
            )
            .order_by(ModelVersion.version_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_next_version_number(self, model_id: UUID) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(ModelVersion.version_number), 0)).where(
                ModelVersion.model_id == model_id
            )
        )
        return result.scalar_one() + 1

    async def create(self, version: ModelVersion) -> ModelVersion:
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def delete(self, version: ModelVersion) -> None:
        self.session.delete(version)
        await self.session.commit()
