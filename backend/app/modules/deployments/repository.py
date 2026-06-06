from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deployment import Deployment, DeploymentEvent, DeploymentStatus


class DeploymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_user(
        self,
        user_id: UUID,
        page: int,
        page_size: int,
        status: DeploymentStatus | None = None,
    ) -> tuple[list[Deployment], int]:
        query = select(Deployment).where(Deployment.user_id == user_id)
        count_query = select(func.count()).select_from(Deployment).where(Deployment.user_id == user_id)

        if status is not None:
            query = query.where(Deployment.status == status)
            count_query = count_query.where(Deployment.status == status)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()
        result = await self.session.execute(
            query.order_by(Deployment.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, deployment_id: UUID, user_id: UUID) -> Deployment | None:
        result = await self.session.execute(
            select(Deployment).where(Deployment.id == deployment_id, Deployment.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, deployment: Deployment) -> Deployment:
        self.session.add(deployment)
        await self.session.commit()
        await self.session.refresh(deployment)
        return deployment

    async def save(self, deployment: Deployment) -> Deployment:
        await self.session.commit()
        await self.session.refresh(deployment)
        return deployment

    async def delete(self, deployment: Deployment) -> None:
        await self.session.delete(deployment)
        await self.session.commit()


class DeploymentEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_deployment(self, deployment_id: UUID) -> list[DeploymentEvent]:
        result = await self.session.execute(
            select(DeploymentEvent)
            .where(DeploymentEvent.deployment_id == deployment_id)
            .order_by(DeploymentEvent.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, event: DeploymentEvent) -> DeploymentEvent:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event
