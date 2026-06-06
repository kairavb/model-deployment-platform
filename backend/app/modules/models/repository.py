from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model import MLModel
from app.models.model_version import ModelVersion


class ModelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_user(self, user_id: UUID, page: int, page_size: int) -> tuple[list[MLModel], int]:
        query = select(MLModel).where(MLModel.user_id == user_id).order_by(MLModel.created_at.desc())
        total_result = await self.session.execute(
            select(func.count()).select_from(MLModel).where(MLModel.user_id == user_id)
        )
        total = total_result.scalar_one()
        result = await self.session.execute(query.offset((page - 1) * page_size).limit(page_size))
        return list(result.scalars().all()), total

    async def get_by_id(self, model_id: UUID, user_id: UUID) -> MLModel | None:
        result = await self.session.execute(
            select(MLModel).where(MLModel.id == model_id, MLModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, model: MLModel) -> MLModel:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete(self, model: MLModel) -> None:
        await self.session.delete(model)
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

    async def create(self, version: ModelVersion) -> ModelVersion:
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def delete(self, version: ModelVersion) -> None:
        await self.session.delete(version)
        await self.session.commit()
