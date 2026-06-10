from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey


class ApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_user(self, user_id: UUID) -> list[ApiKey]:
        result = await self.session.execute(
            select(ApiKey)
            .where(ApiKey.user_id == user_id)
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, key_id: UUID, user_id: UUID) -> ApiKey | None:
        result = await self.session.execute(
            select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_hash(self, key_hash: str) -> ApiKey | None:
        result = await self.session.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.revoked_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, api_key: ApiKey) -> ApiKey:
        self.session.add(api_key)
        await self.session.commit()
        await self.session.refresh(api_key)
        return api_key

    async def save(self, api_key: ApiKey) -> ApiKey:
        await self.session.commit()
        await self.session.refresh(api_key)
        return api_key

    async def revoke(self, api_key: ApiKey) -> ApiKey:
        api_key.revoked_at = datetime.now(UTC)
        return await self.save(api_key)

    async def touch_last_used(self, api_key: ApiKey) -> None:
        api_key.last_used_at = datetime.now(UTC)
        await self.save(api_key)
