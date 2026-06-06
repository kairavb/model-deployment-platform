from uuid import UUID

from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import TokenResponse, UserCreate, UserLogin, UserResponse


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def register(self, payload: UserCreate) -> UserResponse:
        raise NotImplementedError("Registration logic not implemented yet.")

    async def login(self, payload: UserLogin) -> TokenResponse:
        raise NotImplementedError("Login logic not implemented yet.")

    async def get_profile(self, user_id: UUID) -> UserResponse:
        raise NotImplementedError("Profile retrieval not implemented yet.")
