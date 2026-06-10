import logging
from uuid import UUID

from app.core.exceptions import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import TokenResponse, UserCreate, UserLogin, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def register(self, payload: UserCreate) -> UserResponse:
        existing = await self.repository.get_by_email(payload.email)
        if existing is not None:
            raise AppError("Email is already registered.", "EMAIL_EXISTS", 409)

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name,
        )
        created = await self.repository.create(user)
        logger.info("User registered: %s", created.id)
        return UserResponse.model_validate(created)

    async def login(self, payload: UserLogin) -> TokenResponse:
        user = await self.repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AppError("Invalid email or password.", "INVALID_CREDENTIALS", 401)

        token = create_access_token(user.id)
        logger.info("User logged in: %s", user.id)
        return TokenResponse(access_token=token)

    async def get_profile(self, user_id: UUID) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise AppError("User not found.", "USER_NOT_FOUND", 404)
        return UserResponse.model_validate(user)
