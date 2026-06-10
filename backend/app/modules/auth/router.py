from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user, get_current_user_id, get_db
from app.models.user import User
from app.modules.auth.api_key_repository import ApiKeyRepository
from app.modules.auth.api_key_schemas import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse
from app.modules.auth.api_key_service import ApiKeyService
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth")


def get_auth_service(db=Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


def get_api_key_service(db=Depends(get_db)) -> ApiKeyService:
    return ApiKeyService(ApiKeyRepository(db))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, service: AuthService = Depends(get_auth_service)) -> UserResponse:
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return await service.login(payload)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(
    user_id: UUID = Depends(get_current_user_id),
    service: ApiKeyService = Depends(get_api_key_service),
) -> list[ApiKeyResponse]:
    return await service.list_keys(user_id)


@router.post("/api-keys", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKeyCreatedResponse:
    return await service.create_key(user_id, payload)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ApiKeyService = Depends(get_api_key_service),
) -> None:
    await service.revoke_key(user_id, key_id)
