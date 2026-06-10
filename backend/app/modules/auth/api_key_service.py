from uuid import UUID

from app.core.exceptions import AppError
from app.core.security import generate_api_key
from app.models.api_key import ApiKey
from app.modules.auth.api_key_repository import ApiKeyRepository
from app.modules.auth.api_key_schemas import ApiKeyCreatedResponse, ApiKeyCreate, ApiKeyResponse


class ApiKeyService:
    def __init__(self, repository: ApiKeyRepository) -> None:
        self.repository = repository

    async def list_keys(self, user_id: UUID) -> list[ApiKeyResponse]:
        keys = await self.repository.list_by_user(user_id)
        return [ApiKeyResponse.model_validate(key) for key in keys if key.revoked_at is None]

    async def create_key(self, user_id: UUID, payload: ApiKeyCreate) -> ApiKeyCreatedResponse:
        full_key, key_prefix, key_hash = generate_api_key()
        api_key = ApiKey(
            user_id=user_id,
            name=payload.name,
            key_prefix=key_prefix,
            key_hash=key_hash,
        )
        created = await self.repository.create(api_key)
        response = ApiKeyCreatedResponse.model_validate(created)
        response.key = full_key
        return response

    async def revoke_key(self, user_id: UUID, key_id: UUID) -> None:
        api_key = await self.repository.get_by_id(key_id, user_id)
        if api_key is None:
            raise AppError("API key not found.", "API_KEY_NOT_FOUND", 404)
        if api_key.revoked_at is not None:
            raise AppError("API key is already revoked.", "API_KEY_REVOKED", 409)
        await self.repository.revoke(api_key)
