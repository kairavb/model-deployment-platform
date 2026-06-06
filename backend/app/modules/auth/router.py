from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth")


def get_auth_service(db=Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, service: AuthService = Depends(get_auth_service)) -> UserResponse:
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return await service.login(payload)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
